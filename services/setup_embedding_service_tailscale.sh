#!/bin/bash
# Setup Embedding Service with Tailscale Access
# This script configures the embedding service and exposes it via Tailscale

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.aya.embedding-service.plist"
TAILSCALE_BIN="/Applications/Tailscale.app/Contents/MacOS/Tailscale"

echo "🚀 Setting up AYA Embedding Service with Tailscale access..."

# Step 1: Copy LaunchAgent plist
echo "📋 Installing LaunchAgent..."
cp "$SCRIPT_DIR/com.aya.embedding-service.plist" "$PLIST_PATH"
chmod 644 "$PLIST_PATH"

# Step 2: Load LaunchAgent
echo "🔄 Loading LaunchAgent service..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 5

# Step 3: Verify service is running
if curl -s http://localhost:8765/health > /dev/null 2>&1; then
    echo "✅ Embedding service is running on localhost:8765"
else
    echo "⚠️  Service may still be starting. Check logs:"
    echo "   tail -f ~/Library/Logs/AgentTurbo/embedding.log"
fi

# Step 4: Configure Tailscale Serve (if Tailscale is available)
if [ -f "$TAILSCALE_BIN" ]; then
    echo "🌐 Configuring Tailscale Serve for embedding service..."
    
    # Get hostname
    HOSTNAME=$(hostname)
    TAILSCALE_HOST="${HOSTNAME}.tail5f2bae.ts.net"
    
    echo "   Hostname: $TAILSCALE_HOST"
    echo "   Port: 8765"
    
    # Note: Tailscale Serve configuration requires admin privileges
    # User needs to run this manually or via sudo
    echo ""
    echo "📝 To expose via Tailscale, run:"
    echo "   sudo $TAILSCALE_BIN serve --bg --set-path=/embedding --http=8765"
    echo ""
    echo "   Or configure via Tailscale admin console:"
    echo "   https://login.tailscale.com/admin/machines"
    echo ""
    echo "   Access URL will be:"
    echo "   https://${TAILSCALE_HOST}/embedding"
    echo ""
else
    echo "⚠️  Tailscale not found at $TAILSCALE_BIN"
    echo "   Install Tailscale or update TAILSCALE_BIN path in this script"
fi

# Step 5: Test service
echo ""
echo "🧪 Testing embedding service..."
if curl -s http://localhost:8765/health | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Health check passed"
    curl -s http://localhost:8765/health | python3 -m json.tool
else
    echo "❌ Health check failed - check logs"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Service Management:"
echo "   Start:   launchctl load $PLIST_PATH"
echo "   Stop:    launchctl unload $PLIST_PATH"
echo "   Restart: launchctl unload $PLIST_PATH && launchctl load $PLIST_PATH"
echo "   Logs:    tail -f ~/Library/Logs/AgentTurbo/embedding.log"
echo ""
echo "🌐 Tailscale Access:"
echo "   Local:   http://localhost:8765"
echo "   Remote:  https://${TAILSCALE_HOST}/embedding (after Tailscale serve config)"

