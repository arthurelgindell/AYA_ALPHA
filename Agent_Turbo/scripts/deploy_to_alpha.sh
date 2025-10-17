#!/bin/bash
# Deploy Agent Turbo from BETA to ALPHA
# Run this script on BETA to sync to ALPHA

set -e

ALPHA_IP="100.106.170.128"
BETA_SOURCE="/Volumes/DATA/Agent_Turbo"
ALPHA_TARGET="/Volumes/DATA/Agent_Turbo"
ALPHA_USER="arthurdell"  # Adjust if needed

echo "🚀 Agent Turbo Deployment: BETA → ALPHA"
echo "========================================"
echo "Source: $BETA_SOURCE"
echo "Target: $ALPHA_USER@$ALPHA_IP:$ALPHA_TARGET"
echo ""

# Verify source exists
if [ ! -d "$BETA_SOURCE" ]; then
    echo "❌ Source directory not found: $BETA_SOURCE"
    exit 1
fi

# Test ALPHA connectivity
echo "[1/5] Testing ALPHA connectivity..."
if ping -c 1 -W 2 "$ALPHA_IP" > /dev/null 2>&1; then
    echo "✅ ALPHA reachable at $ALPHA_IP"
else
    echo "❌ Cannot reach ALPHA at $ALPHA_IP"
    exit 1
fi

# Create target directory on ALPHA
echo "[2/5] Creating target directory on ALPHA..."
ssh "$ALPHA_USER@$ALPHA_IP" "mkdir -p $ALPHA_TARGET" || {
    echo "❌ Failed to create directory on ALPHA"
    exit 1
}
echo "✅ Target directory ready"

# Rsync Agent Turbo folder
echo "[3/5] Syncing Agent Turbo folder..."
rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'data/agent_turbo.db' \
    "$BETA_SOURCE/" \
    "$ALPHA_USER@$ALPHA_IP:$ALPHA_TARGET/" || {
    echo "❌ Rsync failed"
    exit 1
}
echo "✅ Files synced successfully"

# Verify config file exists
echo "[4/5] Verifying ALPHA config..."
ssh "$ALPHA_USER@$ALPHA_IP" "test -f $ALPHA_TARGET/config/alpha_config.py" && {
    echo "✅ ALPHA config file present"
} || {
    echo "⚠️  ALPHA config file not found (will use defaults)"
}

# Run verification on ALPHA
echo "[5/5] Running verification on ALPHA..."
ssh "$ALPHA_USER@$ALPHA_IP" "cd $ALPHA_TARGET && python3 core/agent_turbo.py verify" && {
    echo "✅ Agent Turbo verified on ALPHA"
} || {
    echo "⚠️  Verification failed (may need dependencies installed)"
}

echo ""
echo "========================================"
echo "✅ Deployment Complete"
echo ""
echo "Next steps on ALPHA:"
echo "1. Install dependencies: pip3 install mlx psutil requests psycopg2-binary"
echo "2. Verify LM Studio running: curl http://localhost:1234/v1/models"
echo "3. Optional: Create RAM disk at /Volumes/DATA/Agent_RAM"
echo "4. Run benchmark: python3 $ALPHA_TARGET/core/agent_turbo.py stats"
echo ""
echo "Note: Each system maintains independent Agent Turbo cache"
echo "PostgreSQL aya_rag remains single source of truth ✅"

