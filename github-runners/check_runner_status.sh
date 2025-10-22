#!/bin/bash
#
# GitHub Actions Runner Status Check
# Verify both ALPHA and BETA runners are operational
#

echo "========================================================================"
echo "GitHub Actions Runner Status Check"
echo "========================================================================"
echo "Date: $(date)"
echo ""

# Check ALPHA runner
echo "ALPHA Runner ($(hostname)):"
ALPHA_PID=$(ps aux | grep Runner.Listener | grep -v grep | awk '{print $2}')
if [ -n "$ALPHA_PID" ]; then
    echo "  ✅ Runner process running (PID: $ALPHA_PID)"
    
    # Get runner name and labels
    RUNNER_NAME=$(tail -100 /Users/runner/actions-runner/_diag/Runner_*.log 2>/dev/null | grep "Arg 'name'" | tail -1 | grep -oE "'[^']+'" | tail -1 | tr -d "'")
    RUNNER_LABELS=$(tail -100 /Users/runner/actions-runner/_diag/Runner_*.log 2>/dev/null | grep "Arg 'labels'" | tail -1 | grep -oE "'[^']+'" | tail -1 | tr -d "'")
    
    echo "  Name: $RUNNER_NAME"
    echo "  Labels: $RUNNER_LABELS"
    
    # Check if launchd service is running
    if launchctl list | grep -q actions.runner; then
        echo "  ✅ LaunchDaemon configured (will auto-restart)"
    else
        echo "  ⚠️  LaunchDaemon not configured (manual restart required)"
    fi
else
    echo "  ❌ Runner NOT running"
    echo "  Fix: cd /Users/runner/actions-runner && sudo ./svc.sh start"
fi

echo ""

# Check BETA runner
echo "BETA Runner (beta.local):"
BETA_PID=$(ssh beta.local "ps aux | grep Runner.Listener | grep -v grep | awk '{print \$2}'" 2>/dev/null)
if [ -n "$BETA_PID" ]; then
    echo "  ✅ Runner process running (PID: $BETA_PID)"
    
    # Get runner name and labels
    RUNNER_NAME=$(ssh beta.local "tail -100 /Users/runner/actions-runner/_diag/Runner_*.log 2>/dev/null | grep \"Arg 'name'\" | tail -1 | grep -oE \"'[^']+\" | tail -1 | tr -d \"'\"" 2>/dev/null)
    RUNNER_LABELS=$(ssh beta.local "tail -100 /Users/runner/actions-runner/_diag/Runner_*.log 2>/dev/null | grep \"Arg 'labels'\" | tail -1 | grep -oE \"'[^']+\" | tail -1 | tr -d \"'\"" 2>/dev/null)
    
    echo "  Name: $RUNNER_NAME"
    echo "  Labels: $RUNNER_LABELS"
    
    # Check if launchd service is running
    if ssh beta.local "launchctl list | grep -q actions.runner" 2>/dev/null; then
        echo "  ✅ LaunchDaemon configured (will auto-restart)"
    else
        echo "  ⚠️  LaunchDaemon not configured (manual restart required)"
    fi
else
    echo "  ❌ Runner NOT running on BETA"
    echo "  Fix: ssh beta.local 'cd /Users/runner/actions-runner && sudo ./svc.sh start'"
fi

echo ""

# Network connectivity test
echo "Network Connectivity (BETA → ALPHA):"
if ssh beta.local "ping -c 2 -t 5 alpha.local" &>/dev/null; then
    echo "  ✅ Network connectivity confirmed"
else
    echo "  ⚠️  Network connectivity issue"
fi

echo ""

# Summary
echo "========================================================================"
if [ -n "$ALPHA_PID" ] && [ -n "$BETA_PID" ]; then
    echo "✅ BOTH RUNNERS OPERATIONAL"
    echo "   Ready for GitHub Actions workflows"
else
    echo "❌ ONE OR MORE RUNNERS DOWN"
    echo "   GitHub Actions workflows will fail"
fi
echo "========================================================================"

