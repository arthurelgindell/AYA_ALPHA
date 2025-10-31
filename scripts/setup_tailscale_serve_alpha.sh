#!/bin/bash
# Tailscale Serve Setup for ALPHA
# Configures all web services to be accessible via Tailscale network
# Run after reboot to ensure all services are exposed

set -e

TAILSCALE="/Applications/Tailscale.app/Contents/MacOS/Tailscale"

echo "=== ALPHA Tailscale Serve Setup ==="
echo "Timestamp: $(date)"
echo ""

# Check if Tailscale is running
if ! pgrep -x "Tailscale" > /dev/null; then
    echo "ERROR: Tailscale is not running. Start Tailscale first."
    exit 1
fi

echo "Configuring Tailscale Serve for ALPHA services..."

# LM Studio (already configured, included for completeness)
echo "  - LM Studio (port 1234) → https://alpha.tail5f2bae.ts.net/"
$TAILSCALE serve --bg 1234 2>&1 | grep -v "already" || true

# Embedding Service
echo "  - Embedding Service (port 8765) → https://alpha.tail5f2bae.ts.net:8765/"
$TAILSCALE serve --bg --https 8765 http://127.0.0.1:8765 2>&1 | grep -v "already" || true

# Database UI (PostgreSQL monitoring - if needed)
# echo "  - Database monitoring (if configured)"

echo ""
echo "=== Configuration Complete ==="
echo ""
echo "Current Tailscale Serve Status:"
$TAILSCALE serve status
echo ""
echo "All ALPHA services are now accessible via Tailscale network."
