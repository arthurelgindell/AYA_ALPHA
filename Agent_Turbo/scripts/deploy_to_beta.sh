#!/bin/bash
# Deploy Agent Turbo Parallel Execution to BETA
# Phase 2: Scale to 10 concurrent (5 ALPHA + 5 BETA)

set -e

BETA_IP="100.84.202.68"  # beta.tail5f2bae.ts.net
BETA_USER="arthurdell"
ALPHA_SOURCE="/Users/arthurdell/AYA/Agent_Turbo"

echo "═══════════════════════════════════════════════════════════════════"
echo "  Phase 2: BETA Deployment - Parallel Agent Execution"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Source: $ALPHA_SOURCE"
echo "Target: $BETA_USER@$BETA_IP"
echo ""

# Test connectivity
echo "[1/6] Testing BETA connectivity..."
if ping -c 1 -W 2 "$BETA_IP" > /dev/null 2>&1; then
    echo "✅ BETA reachable"
else
    echo "❌ Cannot reach BETA"
    exit 1
fi

# Sync core files
echo ""
echo "[2/6] Syncing core execution files..."
rsync -avz --progress \
    "$ALPHA_SOURCE/core/task_worker.py" \
    "$ALPHA_SOURCE/core/claude_executor.py" \
    "$ALPHA_SOURCE/core/task_api.py" \
    "$ALPHA_SOURCE/core/postgres_connector.py" \
    "$BETA_USER@$BETA_IP:/Volumes/DATA/AYA/Agent_Turbo/core/"

echo "✅ Core files synced"

# Sync migration
echo ""
echo "[3/6] Syncing database migration..."
ssh "$BETA_USER@$BETA_IP" "mkdir -p /Volumes/DATA/AYA/Agent_Turbo/migrations"
rsync -avz \
    "$ALPHA_SOURCE/migrations/001_add_task_execution_fields.sql" \
    "$BETA_USER@$BETA_IP:/Volumes/DATA/AYA/Agent_Turbo/migrations/"

echo "✅ Migration synced"

# Create log directory
echo ""
echo "[4/6] Creating log directory on BETA..."
ssh "$BETA_USER@$BETA_IP" "mkdir -p ~/Library/Logs/AgentTurbo && chmod 755 ~/Library/Logs/AgentTurbo"
echo "✅ Log directory created"

# Deploy launchd service
echo ""
echo "[5/6] Deploying launchd service to BETA..."

# Create the plist directly on BETA via ssh
ssh "$BETA_USER@$BETA_IP" "cat > ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist" << 'EOPLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aya.agent-turbo-worker</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Volumes/DATA/AYA/Agent_Turbo/core/task_worker.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Volumes/DATA/AYA/Agent_Turbo/core</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>MAX_CONCURRENT_AGENTS</key>
        <string>5</string>
        <key>POLL_INTERVAL</key>
        <string>1.0</string>
        <key>PGPASSWORD</key>
        <string>Power$$336633$$</string>
        <key>PATH</key>
        <string>/Users/arthurdell/.nvm/versions/node/v24.9.0/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/Users/arthurdell/Library/Logs/AgentTurbo/worker.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/arthurdell/Library/Logs/AgentTurbo/worker.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
EOPLIST

echo "✅ LaunchAgent plist created on BETA"

# Start service
echo ""
echo "[6/6] Starting worker service on BETA..."
ssh "$BETA_USER@$BETA_IP" "launchctl load ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist 2>&1 || launchctl start com.aya.agent-turbo-worker"

sleep 3

# Verify service
echo ""
echo "Verifying BETA worker service..."
ssh "$BETA_USER@$BETA_IP" "launchctl list | grep agent-turbo-worker"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  ✅ Phase 2 Deployment Complete"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "BETA Worker Status:"
ssh "$BETA_USER@$BETA_IP" "launchctl list | grep agent-turbo"
echo ""
echo "Total Capacity: 10 concurrent (5 ALPHA + 5 BETA)"
echo ""
echo "Check BETA logs:"
echo "  ssh $BETA_USER@$BETA_IP 'tail -f ~/Library/Logs/AgentTurbo/worker.log'"
echo ""

