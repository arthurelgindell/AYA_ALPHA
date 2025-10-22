#!/bin/bash
#
# Install GitHub Actions Runners as LaunchDaemon Services
# Run with: sudo ./install_runner_services.sh
#

set -e

if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "========================================================================"
echo "Installing GitHub Actions Runners as Services"
echo "========================================================================"
echo ""

# Install ALPHA runner
echo "Installing ALPHA runner service..."
cd /Users/runner/actions-runner

# Stop if running
./svc.sh stop 2>/dev/null || true

# Install service
./svc.sh install

# Start service
./svc.sh start

# Verify
sleep 2
./svc.sh status

echo ""
echo "✅ ALPHA runner service installed"
echo ""

# Install BETA runner (via SSH)
echo "Installing BETA runner service..."
ssh beta.local 'cd /Users/runner/actions-runner && sudo ./svc.sh stop 2>/dev/null || true'
ssh beta.local 'cd /Users/runner/actions-runner && sudo ./svc.sh install'
ssh beta.local 'cd /Users/runner/actions-runner && sudo ./svc.sh start'

# Verify
sleep 2
ssh beta.local 'cd /Users/runner/actions-runner && sudo ./svc.sh status'

echo ""
echo "✅ BETA runner service installed"
echo ""

# Final verification
echo "========================================================================"
echo "Final Verification"
echo "========================================================================"
echo ""

# Check ALPHA
if launchctl list | grep -q actions.runner.arthurelgindell-AYA.alpha-m3-ultra; then
    echo "✅ ALPHA: LaunchDaemon configured"
else
    echo "❌ ALPHA: LaunchDaemon NOT configured"
fi

# Check BETA
if ssh beta.local "launchctl list | grep -q actions.runner.arthurelgindell-AYA.beta-m3-ultra"; then
    echo "✅ BETA: LaunchDaemon configured"
else
    echo "❌ BETA: LaunchDaemon NOT configured"
fi

echo ""

# Check running processes
ALPHA_PID=$(ps aux | grep Runner.Listener | grep -v grep | awk '{print $2}')
BETA_PID=$(ssh beta.local "ps aux | grep Runner.Listener | grep -v grep | awk '{print \$2}'")

if [ -n "$ALPHA_PID" ]; then
    echo "✅ ALPHA: Runner process running (PID: $ALPHA_PID)"
else
    echo "⚠️  ALPHA: Runner process not detected yet (may still be starting)"
fi

if [ -n "$BETA_PID" ]; then
    echo "✅ BETA: Runner process running (PID: $BETA_PID)"
else
    echo "⚠️  BETA: Runner process not detected yet (may still be starting)"
fi

echo ""
echo "========================================================================"
echo "Installation Complete"
echo "========================================================================"
echo ""
echo "Runners are now installed as LaunchDaemon services."
echo "They will:"
echo "  - Auto-start on system boot"
echo "  - Auto-restart if they crash"
echo "  - Run even when no user is logged in"
echo ""
echo "To check status anytime:"
echo "  /Users/arthurdell/AYA/github-runners/check_runner_status.sh"
echo ""
echo "To restart services if needed:"
echo "  ALPHA: sudo launchctl kickstart -k system/actions.runner.arthurelgindell-AYA.alpha-m3-ultra"
echo "  BETA:  ssh beta.local 'sudo launchctl kickstart -k system/actions.runner.arthurelgindell-AYA.beta-m3-ultra'"
echo ""

