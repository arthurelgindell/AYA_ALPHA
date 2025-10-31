#!/bin/bash
#
# Install Git Auto-Sync Service
# Sets up launchd to automatically sync AYA repo to GitHub
#
# Author: Claude for Arthur
# Date: October 29, 2025

set -e

echo "=== Installing Git Auto-Sync Service ==="
echo ""

# Make sync script executable
chmod +x /Users/arthurdell/AYA/scripts/auto_git_sync.sh
echo "✅ Made sync script executable"

# Create logs directory
mkdir -p /Users/arthurdell/AYA/logs
echo "✅ Created logs directory"

# Copy plist to LaunchAgents
PLIST_SOURCE="/Users/arthurdell/AYA/scripts/com.aya.git.autosync.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.aya.git.autosync.plist"

cp "$PLIST_SOURCE" "$PLIST_DEST"
echo "✅ Installed launchd plist"

# Unload if already loaded
if launchctl list | grep -q "com.aya.git.autosync"; then
    echo "⚠️  Service already loaded, unloading..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Load the service
launchctl load "$PLIST_DEST"
echo "✅ Loaded launchd service"

# Verify it's running
sleep 2
if launchctl list | grep -q "com.aya.git.autosync"; then
    echo "✅ Service is running"
else
    echo "❌ Service failed to start"
    exit 1
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "The service will:"
echo "  - Run every 15 minutes"
echo "  - Auto-commit and push changes to GitHub"
echo "  - Log to: /Users/arthurdell/AYA/logs/git_sync.log"
echo ""
echo "To check status:"
echo "  launchctl list | grep com.aya.git.autosync"
echo ""
echo "To view logs:"
echo "  tail -f /Users/arthurdell/AYA/logs/git_sync.log"
echo ""
echo "To stop:"
echo "  launchctl unload ~/Library/LaunchAgents/com.aya.git.autosync.plist"
echo ""
echo "To test manually:"
echo "  /Users/arthurdell/AYA/scripts/auto_git_sync.sh --dry-run"
echo ""

