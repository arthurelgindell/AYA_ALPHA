#!/bin/bash
set -euo pipefail

#===============================================================================
# GitHub Actions Self-Hosted Runner Setup
# For Mac Studio M3 Ultra (ARM64) - macOS
#
# Usage:
#   sudo ./setup-github-runner.sh <HOSTNAME> <GITHUB_TOKEN> <ORG_NAME> <REPO_NAME>
#
# Arguments:
#   HOSTNAME      - Either "ALPHA" or "BETA"
#   GITHUB_TOKEN  - GitHub Personal Access Token with admin:org scope
#   ORG_NAME      - GitHub organization name
#   REPO_NAME     - GitHub repository name (optional, for repo-level runner)
#
# Example:
#   sudo ./setup-github-runner.sh ALPHA ghp_xxxxx myorg myrepo
#===============================================================================

# Configuration
RUNNER_VERSION="2.325.0"
RUNNER_USER="runner"
RUNNER_HOME="/Users/${RUNNER_USER}/actions-runner"
RUNNER_NAME=""
RUNNER_LABELS=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Parse arguments
if [ $# -lt 3 ]; then
    log_error "Usage: $0 <HOSTNAME> <GITHUB_TOKEN> <ORG_NAME> [REPO_NAME]"
    exit 1
fi

HOSTNAME_ARG=$1
GITHUB_TOKEN=$2
ORG_NAME=$3
REPO_NAME=${4:-}

# Validate hostname
if [ "$HOSTNAME_ARG" != "ALPHA" ] && [ "$HOSTNAME_ARG" != "BETA" ]; then
    log_error "HOSTNAME must be either 'ALPHA' or 'BETA'"
    exit 1
fi

# Set runner configuration based on hostname
if [ "$HOSTNAME_ARG" == "ALPHA" ]; then
    RUNNER_NAME="alpha-studio"
    RUNNER_LABELS="self-hosted,macOS,arm64,alpha,studio"
elif [ "$HOSTNAME_ARG" == "BETA" ]; then
    RUNNER_NAME="beta-studio"
    RUNNER_LABELS="self-hosted,macOS,arm64,beta,studio"
fi

log_info "Setting up GitHub Actions runner for $HOSTNAME_ARG"
log_info "Runner name: $RUNNER_NAME"
log_info "Labels: $RUNNER_LABELS"

#===============================================================================
# Step 1: Create runner user
#===============================================================================
log_info "Step 1: Creating runner user"

if id "$RUNNER_USER" &>/dev/null; then
    log_warn "User '$RUNNER_USER' already exists, skipping creation"
else
    # Find next available UID
    NEXT_UID=$(dscl . -list /Users UniqueID | awk '{print $2}' | sort -n | tail -1)
    NEXT_UID=$((NEXT_UID + 1))

    # Create user
    dscl . -create /Users/$RUNNER_USER
    dscl . -create /Users/$RUNNER_USER UserShell /bin/bash
    dscl . -create /Users/$RUNNER_USER RealName "GitHub Actions Runner"
    dscl . -create /Users/$RUNNER_USER UniqueID $NEXT_UID
    dscl . -create /Users/$RUNNER_USER PrimaryGroupID 20
    dscl . -create /Users/$RUNNER_USER NFSHomeDirectory /Users/$RUNNER_USER

    # Create home directory
    createhomedir -c -u $RUNNER_USER

    log_info "User '$RUNNER_USER' created successfully"
fi

#===============================================================================
# Step 2: Download and install runner
#===============================================================================
log_info "Step 2: Downloading GitHub Actions runner $RUNNER_VERSION"

RUNNER_ARCH="osx-arm64"
RUNNER_TAR="actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_TAR}"

# Create runner directory
mkdir -p "$RUNNER_HOME"
cd "$RUNNER_HOME"

# Download runner if not already present
if [ ! -f "$RUNNER_TAR" ]; then
    log_info "Downloading runner from $RUNNER_URL"
    curl -o "$RUNNER_TAR" -L "$RUNNER_URL"
else
    log_warn "Runner tarball already exists, skipping download"
fi

# Extract runner
if [ ! -f "run.sh" ]; then
    log_info "Extracting runner"
    tar xzf "$RUNNER_TAR"
else
    log_warn "Runner already extracted, skipping extraction"
fi

# Set ownership
chown -R $RUNNER_USER:staff "$RUNNER_HOME"

#===============================================================================
# Step 3: Configure runner
#===============================================================================
log_info "Step 3: Configuring runner"

# Generate registration token
if [ -n "$REPO_NAME" ]; then
    # Repository-level runner
    log_info "Configuring as repository-level runner for $ORG_NAME/$REPO_NAME"
    RUNNER_URL_CONFIG="https://github.com/$ORG_NAME/$REPO_NAME"
    TOKEN_URL="https://api.github.com/repos/$ORG_NAME/$REPO_NAME/actions/runners/registration-token"
else
    # Organization-level runner
    log_info "Configuring as organization-level runner for $ORG_NAME"
    RUNNER_URL_CONFIG="https://github.com/$ORG_NAME"
    TOKEN_URL="https://api.github.com/orgs/$ORG_NAME/actions/runners/registration-token"
fi

log_info "Generating registration token"
REGISTRATION_TOKEN=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "$TOKEN_URL" | grep -o '"token": "[^"]*' | cut -d'"' -f4)

if [ -z "$REGISTRATION_TOKEN" ]; then
    log_error "Failed to generate registration token. Check your GitHub token permissions."
    exit 1
fi

# Configure runner (run as runner user)
log_info "Registering runner with GitHub"
sudo -u $RUNNER_USER ./config.sh \
    --url "$RUNNER_URL_CONFIG" \
    --token "$REGISTRATION_TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "$RUNNER_LABELS" \
    --work _work \
    --unattended \
    --replace \
    --disableupdate

log_info "Runner configured successfully"

#===============================================================================
# Step 4: Create .runnerconfig for hardening
#===============================================================================
log_info "Step 4: Creating runner configuration"

cat > "$RUNNER_HOME/.runnerconfig" << 'EOF'
{
  "disableUpdate": true,
  "ephemeral": false,
  "workFolder": "_work"
}
EOF

chown $RUNNER_USER:staff "$RUNNER_HOME/.runnerconfig"

#===============================================================================
# Step 5: Create launchd service
#===============================================================================
log_info "Step 5: Creating launchd service"

PLIST_PATH="/Users/$RUNNER_USER/Library/LaunchAgents/com.github.actions.runner.plist"
mkdir -p "/Users/$RUNNER_USER/Library/LaunchAgents"

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.actions.runner</string>

    <key>ProgramArguments</key>
    <array>
        <string>${RUNNER_HOME}/run.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>WorkingDirectory</key>
    <string>${RUNNER_HOME}</string>

    <key>StandardOutPath</key>
    <string>${RUNNER_HOME}/runner.out.log</string>

    <key>StandardErrorPath</key>
    <string>${RUNNER_HOME}/runner.err.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>ProcessType</key>
    <string>Interactive</string>

    <key>Nice</key>
    <integer>-10</integer>
</dict>
</plist>
EOF

chown $RUNNER_USER:staff "$PLIST_PATH"
chmod 644 "$PLIST_PATH"

log_info "launchd service created at $PLIST_PATH"

#===============================================================================
# Step 6: Create cleanup script
#===============================================================================
log_info "Step 6: Creating cleanup script"

cat > "$RUNNER_HOME/cleanup-work.sh" << 'EOF'
#!/bin/bash
# Cleanup _work directory between runs
# Run this periodically via cron or launchd

WORK_DIR="$HOME/actions-runner/_work"

if [ -d "$WORK_DIR" ]; then
    echo "Cleaning up $WORK_DIR"
    find "$WORK_DIR" -type d -name ".git" -prune -o -type f -mtime +7 -delete
    find "$WORK_DIR" -type d -empty -delete
    echo "Cleanup complete"
else
    echo "Work directory not found: $WORK_DIR"
fi
EOF

chmod +x "$RUNNER_HOME/cleanup-work.sh"
chown $RUNNER_USER:staff "$RUNNER_HOME/cleanup-work.sh"

# Create launchd job for periodic cleanup
CLEANUP_PLIST="/Users/$RUNNER_USER/Library/LaunchAgents/com.github.actions.runner.cleanup.plist"

cat > "$CLEANUP_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.actions.runner.cleanup</string>

    <key>ProgramArguments</key>
    <array>
        <string>${RUNNER_HOME}/cleanup-work.sh</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>${RUNNER_HOME}/cleanup.out.log</string>

    <key>StandardErrorPath</key>
    <string>${RUNNER_HOME}/cleanup.err.log</string>
</dict>
</plist>
EOF

chown $RUNNER_USER:staff "$CLEANUP_PLIST"
chmod 644 "$CLEANUP_PLIST"

log_info "Cleanup script and launchd job created"

#===============================================================================
# Step 7: Start runner service
#===============================================================================
log_info "Step 7: Starting runner service"

# Load launchd service as runner user
sudo -u $RUNNER_USER launchctl load "$PLIST_PATH"
sudo -u $RUNNER_USER launchctl load "$CLEANUP_PLIST"

# Give it a moment to start
sleep 3

# Check if runner is running
if sudo -u $RUNNER_USER launchctl list | grep -q "com.github.actions.runner"; then
    log_info "✅ Runner service started successfully"
else
    log_error "Failed to start runner service"
    log_error "Check logs at $RUNNER_HOME/runner.err.log"
    exit 1
fi

#===============================================================================
# Step 8: Create management scripts
#===============================================================================
log_info "Step 8: Creating management scripts"

# Start script
cat > "$RUNNER_HOME/start-runner.sh" << EOF
#!/bin/bash
launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist
echo "Runner service loaded"
EOF

# Stop script
cat > "$RUNNER_HOME/stop-runner.sh" << EOF
#!/bin/bash
launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist
echo "Runner service unloaded"
EOF

# Status script
cat > "$RUNNER_HOME/status-runner.sh" << EOF
#!/bin/bash
echo "=== Runner Service Status ==="
if launchctl list | grep -q "com.github.actions.runner"; then
    echo "✅ Runner service is loaded"
    launchctl list | grep com.github.actions.runner
else
    echo "❌ Runner service is not loaded"
fi

echo ""
echo "=== Recent Logs ==="
tail -n 20 ~/actions-runner/runner.out.log
EOF

# Logs script
cat > "$RUNNER_HOME/view-logs.sh" << EOF
#!/bin/bash
echo "=== Runner Logs (last 50 lines) ==="
tail -n 50 ~/actions-runner/runner.out.log
echo ""
echo "=== Runner Errors (last 20 lines) ==="
tail -n 20 ~/actions-runner/runner.err.log
EOF

chmod +x "$RUNNER_HOME"/*.sh
chown $RUNNER_USER:staff "$RUNNER_HOME"/*.sh

#===============================================================================
# Step 9: Create hardening README
#===============================================================================
log_info "Step 9: Creating hardening documentation"

cat > "$RUNNER_HOME/HARDENING.md" << 'EOF'
# GitHub Actions Runner Hardening

This runner is configured with the following security measures:

## Repository Access
- Configure repository-specific runners (not organization-wide) when possible
- Use repository rulesets to restrict which workflows can run

## Action Pinning
- Always pin actions to specific commit SHAs, not tags
- Example: `actions/checkout@<full-40-char-sha>`
- Use Dependabot to keep action versions updated

## Token Permissions
- Default GITHUB_TOKEN permissions are read-only
- Escalate permissions per-job using `permissions:` key
- Never store secrets in workflow files

## Fork Pull Requests
- Disallow workflow runs from forks by default
- Require approval for first-time contributors
- Configure in repository settings: Actions > Fork pull request workflows

## Workflow Security
```yaml
# Example secure workflow
name: Secure Workflow
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read  # Default: read-only

jobs:
  build:
    runs-on: [self-hosted, macOS, arm64, studio]
    permissions:
      contents: read
      pull-requests: write  # Escalate only for this job

    steps:
      - uses: actions/checkout@<sha>  # Pin to SHA
      - name: Build
        run: make build
```

## Monitoring
- Check logs: `~/actions-runner/runner.out.log`
- Monitor disk usage in `~/actions-runner/_work`
- Review workflow runs in GitHub UI

## Maintenance
- Update runner: Download new version and re-run config.sh
- Cleanup: `~/actions-runner/cleanup-work.sh` (runs daily at 3 AM)
- Restart: `~/actions-runner/stop-runner.sh && ~/actions-runner/start-runner.sh`

## Additional Recommendations
1. Enable branch protection rules
2. Require code review before merging
3. Use environment secrets for sensitive data
4. Regularly audit workflow permissions
5. Monitor runner activity in GitHub Actions dashboard
EOF

chown $RUNNER_USER:staff "$RUNNER_HOME/HARDENING.md"

#===============================================================================
# Completion
#===============================================================================
log_info ""
log_info "=========================================="
log_info "✅ GitHub Actions Runner Setup Complete"
log_info "=========================================="
log_info ""
log_info "Runner Details:"
log_info "  Name: $RUNNER_NAME"
log_info "  Labels: $RUNNER_LABELS"
log_info "  Home: $RUNNER_HOME"
log_info "  User: $RUNNER_USER"
log_info ""
log_info "Service Status:"
log_info "  launchd: com.github.actions.runner"
log_info "  Logs: $RUNNER_HOME/runner.out.log"
log_info "  Errors: $RUNNER_HOME/runner.err.log"
log_info ""
log_info "Management Commands (run as $RUNNER_USER):"
log_info "  Start:  $RUNNER_HOME/start-runner.sh"
log_info "  Stop:   $RUNNER_HOME/stop-runner.sh"
log_info "  Status: $RUNNER_HOME/status-runner.sh"
log_info "  Logs:   $RUNNER_HOME/view-logs.sh"
log_info ""
log_info "Hardening Guide:"
log_info "  Read: $RUNNER_HOME/HARDENING.md"
log_info ""
log_info "Next Steps:"
log_info "  1. Verify runner appears in GitHub: Settings > Actions > Runners"
log_info "  2. Run smoke test workflow: .github/workflows/runner-smoke.yml"
log_info "  3. Review hardening documentation"
log_info "  4. Configure repository-specific access if needed"
log_info ""
log_info "=========================================="
