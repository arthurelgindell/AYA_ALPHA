#!/bin/bash
# Agent Turbo Quick Start on ALPHA
# Run this after moving AT_Beta to /Users/arthurdell/AYA/Agent_Turbo

set -e

echo "🚀 Agent Turbo - ALPHA Quick Start"
echo "====================================="
echo ""

# Check Python version
echo "[1/6] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION"

# Install dependencies
echo ""
echo "[2/6] Installing dependencies..."
pip3 install -q mlx mlx-nn psutil requests psycopg2-binary 2>/dev/null && {
    echo "✅ Dependencies installed"
} || {
    echo "⚠️  Some dependencies may already be installed"
}

# Check LM Studio
echo ""
echo "[3/6] Checking LM Studio..."
curl -s http://localhost:1234/v1/models > /dev/null 2>&1 && {
    echo "✅ LM Studio accessible"
} || {
    echo "⚠️  LM Studio not responding (ensure it's running on port 1234)"
}

# Check Apple Silicon
echo ""
echo "[4/6] Checking hardware..."
if system_profiler SPHardwareDataType 2>/dev/null | grep -q "Apple"; then
    echo "✅ Apple Silicon detected (GPU acceleration available)"
else
    echo "⚠️  Non-Apple Silicon (will run in CPU mode)"
fi

# Run verification
echo ""
echo "[5/6] Verifying Agent Turbo..."
python3 Agent_Turbo/core/agent_turbo.py verify && {
    echo "✅ Agent Turbo verified"
} || {
    echo "❌ Verification failed"
    exit 1
}

# Get stats
echo ""
echo "[6/6] Getting system statistics..."
python3 Agent_Turbo/core/agent_turbo.py stats | python3 -m json.tool

echo ""
echo "====================================="
echo "✅ Agent Turbo is OPERATIONAL on ALPHA"
echo ""
echo "Next steps:"
echo "- Test query: python3 Agent_Turbo/core/agent_turbo.py query 'test'"
echo "- Add knowledge: python3 Agent_Turbo/core/agent_turbo.py add 'your knowledge'"
echo "- Full guide: cat ALPHA_DEPLOYMENT_GUIDE.md"

