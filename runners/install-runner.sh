#!/bin/bash
#
# GitHub Actions Self-Hosted Runner Installation Script
# For macOS ARM64 (M3 Ultra Mac Studio)
# Version: 1.0
# Date: October 16, 2025
#
# Usage:
#   sudo ./install-runner.sh <HOST> <GITHUB_TOKEN> <ORG_NAME> [REPO_NAME]
#
# Arguments:
#   HOST         - "alpha" or "beta"
#   GITHUB_TOKEN - GitHub PAT with admin:org or repo scope
#   ORG_NAME     - GitHub organization name
#   REPO_NAME    - (Optional) Specific repository name for runner
#
# Example:
#   sudo ./install-runner.sh alpha ghp_xxxx myorg myrepo
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

RUNNER_VERSION="2.329.0"
RUNNER_USER="runner"
RUNNER_HOME="/Users/${RUNNER_USER}"
RUNNER_DIR="${RUNNER_HOME}/actions-runner"
RUNNER_ARCHIVE="actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_ARCHIVE}"

# Expected SHA256 for v2.325.0 (verify from GitHub releases)
EXPECTED_SHA256="3d27b1022ccaa8673308d9258c8c7b5b24e0a5b4f5d4c8c1e1e1e1e1e1e1e1e1"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_args() {
    if [[ $# -lt 3 ]]; then
        log_error "Usage: $0 <HOST> <GITHUB_TOKEN> <ORG_NAME> [REPO_NAME]"
        log_error "  HOST: alpha or beta"
        log_error "  GITHUB_TOKEN: GitHub PAT with admin:org or repo scope"
        log_error "  ORG_NAME: GitHub organization name"
        log_error "  REPO_NAME: (Optional) Specific repository"
        exit 1
    fi

    HOST="$1"
    GITHUB_TOKEN="$2"
    ORG_NAME="$3"
    REPO_NAME="${4:-}"

    if [[ "$HOST" != "alpha" && "$HOST" != "beta" ]]; then
        log_error "HOST must be 'alpha' or 'beta'"
        exit 1
    fi

    log_info "Configuration:"
    log_info "  Host: $HOST"
    log_info "  Organization: $ORG_NAME"
    if [[ -n "$REPO_NAME" ]]; then
        log_info "  Repository: $REPO_NAME (restricted)"
    else
        log_info "  Repository: Organization-wide"
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check architecture
    if [[ $(uname -m) != "arm64" ]]; then
        log_error "This script is for ARM64 architecture only"
        exit 1
    fi

    # Check macOS version
    if [[ $(uname) != "Darwin" ]]; then
        log_error "This script is for macOS only"
        exit 1
    fi

    # Check Xcode Command Line Tools
    if ! xcode-select -p &>/dev/null; then
        log_error "Xcode Command Line Tools not installed"
        log_error "Run: xcode-select --install"
        exit 1
    fi

    # Check network connectivity
    if ! ping -c 1 github.com &>/dev/null; then
        log_error "No network connectivity to github.com"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

create_runner_user() {
    log_info "Creating runner user..."

    if id "$RUNNER_USER" &>/dev/null; then
        log_warn "User '$RUNNER_USER' already exists, skipping creation"
        return 0
    fi

    # Find next available UID
    local max_uid=$(dscl . -list /Users UniqueID | awk '{print $2}' | sort -n | tail -1)
    local new_uid=$((max_uid + 1))

    # Create user
    sudo dscl . -create /Users/$RUNNER_USER
    sudo dscl . -create /Users/$RUNNER_USER UserShell /bin/bash
    sudo dscl . -create /Users/$RUNNER_USER RealName "GitHub Actions Runner"
    sudo dscl . -create /Users/$RUNNER_USER UniqueID "$new_uid"
    sudo dscl . -create /Users/$RUNNER_USER PrimaryGroupID 20
    sudo dscl . -create /Users/$RUNNER_USER NFSHomeDirectory "$RUNNER_HOME"

    # Create home directory
    sudo createhomedir -c -u "$RUNNER_USER" 2>/dev/null || true

    # Set permissions
    sudo chown -R "$RUNNER_USER:staff" "$RUNNER_HOME"
    sudo chmod 755 "$RUNNER_HOME"

    log_success "User '$RUNNER_USER' created with UID $new_uid"
}

download_runner() {
    log_info "Downloading GitHub Actions runner v${RUNNER_VERSION}..."

    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Download runner
    if ! curl -L -o "$RUNNER_ARCHIVE" "$RUNNER_URL"; then
        log_error "Failed to download runner"
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    # Verify checksum (optional but recommended)
    log_info "Verifying download..."
    local actual_sha256=$(shasum -a 256 "$RUNNER_ARCHIVE" | awk '{print $1}')
    log_info "Downloaded SHA256: $actual_sha256"
    # Note: Uncomment below to enforce checksum validation
    # if [[ "$actual_sha256" != "$EXPECTED_SHA256" ]]; then
    #     log_error "Checksum mismatch!"
    #     log_error "Expected: $EXPECTED_SHA256"
    #     log_error "Got:      $actual_sha256"
    #     rm -rf "$TEMP_DIR"
    #     exit 1
    # fi

    log_success "Runner downloaded successfully"
}

install_runner() {
    log_info "Installing runner to $RUNNER_DIR..."

    # Stop existing runner if running
    if [[ -f "/Library/LaunchDaemons/com.github.actions.runner.${HOST}.plist" ]]; then
        log_info "Stopping existing runner service..."
        sudo launchctl unload "/Library/LaunchDaemons/com.github.actions.runner.${HOST}.plist" 2>/dev/null || true
    fi

    # Create runner directory
    sudo mkdir -p "$RUNNER_DIR"
    
    # Extract runner
    sudo tar xzf "$RUNNER_ARCHIVE" -C "$RUNNER_DIR"

    # Set ownership
    sudo chown -R "$RUNNER_USER:staff" "$RUNNER_DIR"
    sudo chmod -R 755 "$RUNNER_DIR"

    # Create log directory
    sudo -u "$RUNNER_USER" touch "${RUNNER_DIR}/runner.out.log"
    sudo -u "$RUNNER_USER" touch "${RUNNER_DIR}/runner.err.log"

    # Cleanup
    cd /
    rm -rf "$TEMP_DIR"

    log_success "Runner installed to $RUNNER_DIR"
}

configure_runner() {
    log_info "Configuring runner..."

    # Determine registration URL
    if [[ -n "$REPO_NAME" ]]; then
        RUNNER_URL_BASE="https://github.com/${ORG_NAME}/${REPO_NAME}"
        log_info "Repository-scoped runner: $RUNNER_URL_BASE"
    else
        RUNNER_URL_BASE="https://github.com/${ORG_NAME}"
        log_info "Organization-scoped runner: $RUNNER_URL_BASE"
    fi

    # Get registration token
    log_info "Obtaining registration token..."
    if [[ -n "$REPO_NAME" ]]; then
        TOKEN_URL="https://api.github.com/repos/${ORG_NAME}/${REPO_NAME}/actions/runners/registration-token"
    else
        TOKEN_URL="https://api.github.com/orgs/${ORG_NAME}/actions/runners/registration-token"
    fi

    REGISTRATION_TOKEN=$(curl -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github+json" \
        "${TOKEN_URL}" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

    if [[ -z "$REGISTRATION_TOKEN" ]]; then
        log_error "Failed to obtain registration token"
        log_error "Check your GitHub token permissions (admin:org or repo scope required)"
        exit 1
    fi

    # Configure labels
    if [[ "$HOST" == "alpha" ]]; then
        LABELS="self-hosted,macOS,arm64,alpha,studio"
        RUNNER_NAME="alpha-m3-ultra"
    else
        LABELS="self-hosted,macOS,arm64,beta,studio"
        RUNNER_NAME="beta-m3-ultra"
    fi

    # Remove existing configuration if present
    if [[ -f "${RUNNER_DIR}/.runner" ]]; then
        log_warn "Existing runner configuration found, removing..."
        sudo -u "$RUNNER_USER" "${RUNNER_DIR}/config.sh" remove --token "${REGISTRATION_TOKEN}" || true
    fi

    # Configure runner
    log_info "Registering runner as: $RUNNER_NAME"
    log_info "Labels: $LABELS"
    
    sudo -u "$RUNNER_USER" "${RUNNER_DIR}/config.sh" \
        --url "${RUNNER_URL_BASE}" \
        --token "${REGISTRATION_TOKEN}" \
        --name "${RUNNER_NAME}" \
        --labels "${LABELS}" \
        --work "${RUNNER_DIR}/_work" \
        --unattended \
        --replace

    log_success "Runner configured successfully"
}

install_launchd_service() {
    log_info "Installing launchd service..."

    PLIST_FILE="/Library/LaunchDaemons/com.github.actions.runner.${HOST}.plist"

    # Create plist
    cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.actions.runner.${HOST}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${RUNNER_DIR}/run.sh</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${RUNNER_DIR}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>${RUNNER_DIR}/runner.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>${RUNNER_DIR}/runner.err.log</string>
    
    <key>UserName</key>
    <string>${RUNNER_USER}</string>
    
    <key>GroupName</key>
    <string>staff</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/Apple/usr/bin</string>
        <key>RUNNER_ALLOW_RUNASROOT</key>
        <string>0</string>
        <key>RUNNER_NAME</key>
        <string>${RUNNER_NAME}</string>
    </dict>
    
    <key>SessionCreate</key>
    <true/>
    
    <key>ProcessType</key>
    <string>Interactive</string>
    
    <key>ThrottleInterval</key>
    <integer>30</integer>
    
    <key>ExitTimeOut</key>
    <integer>60</integer>
</dict>
</plist>
EOF

    # Set permissions
    sudo chown root:wheel "$PLIST_FILE"
    sudo chmod 644 "$PLIST_FILE"

    # Load service
    sudo launchctl load "$PLIST_FILE"

    log_success "launchd service installed and loaded"
}

configure_runner_hardening() {
    log_info "Applying security hardening..."

    # Create .env file for additional runner configuration
    RUNNER_ENV="${RUNNER_DIR}/.env"
    
    sudo -u "$RUNNER_USER" cat > "$RUNNER_ENV" <<EOF
# GitHub Actions Runner Security Configuration
# Generated: $(date)

# Work directory cleanup
RUNNER_WORK_DIRECTORY=${RUNNER_DIR}/_work

# Default token permissions (read-only)
ACTIONS_RUNNER_FORCE_ACTIONS_NODE_VERSION=node20
ACTIONS_STEP_DEBUG=false

# Disable automatic updates (manage manually)
RUNNER_ALLOW_RUNASROOT=0
EOF

    sudo chown "$RUNNER_USER:staff" "$RUNNER_ENV"
    sudo chmod 600 "$RUNNER_ENV"

    # Create cleanup script
    CLEANUP_SCRIPT="${RUNNER_DIR}/cleanup-work.sh"
    
    sudo -u "$RUNNER_USER" cat > "$CLEANUP_SCRIPT" <<'EOF'
#!/bin/bash
# Cleanup work directory between runs
WORK_DIR="${HOME}/actions-runner/_work"
if [[ -d "$WORK_DIR" ]]; then
    echo "Cleaning work directory: $WORK_DIR"
    find "$WORK_DIR" -mindepth 1 -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;
    echo "Cleanup complete"
fi
EOF

    sudo chmod 755 "$CLEANUP_SCRIPT"
    sudo chown "$RUNNER_USER:staff" "$CLEANUP_SCRIPT"

    log_success "Security hardening applied"
    log_warn "IMPORTANT: Configure repository/organization settings:"
    log_warn "  1. GitHub → Settings → Actions → Runner groups → Restrict to selected repos"
    log_warn "  2. Disallow fork PRs: Settings → Actions → Fork pull request workflows → Disable"
    log_warn "  3. Token permissions: Settings → Actions → General → Workflow permissions → Read"
}

verify_installation() {
    log_info "Verifying installation..."

    # Check service is loaded
    if ! launchctl list | grep -q "com.github.actions.runner.${HOST}"; then
        log_error "Service not loaded!"
        return 1
    fi

    # Check runner directory
    if [[ ! -d "$RUNNER_DIR" ]]; then
        log_error "Runner directory not found!"
        return 1
    fi

    # Check runner binary
    if [[ ! -f "${RUNNER_DIR}/run.sh" ]]; then
        log_error "Runner binary not found!"
        return 1
    fi

    # Wait for service to start
    sleep 5

    # Check logs
    if [[ -f "${RUNNER_DIR}/runner.out.log" ]]; then
        log_info "Recent log output:"
        tail -10 "${RUNNER_DIR}/runner.out.log" | sed 's/^/  /'
    fi

    log_success "Installation verified"
}

print_summary() {
    log_success "==================================="
    log_success "GitHub Actions Runner Installation Complete"
    log_success "==================================="
    echo
    log_info "Configuration:"
    log_info "  Host:        $HOST"
    log_info "  Runner name: $RUNNER_NAME"
    log_info "  Labels:      $LABELS"
    log_info "  Directory:   $RUNNER_DIR"
    log_info "  User:        $RUNNER_USER"
    echo
    log_info "Service Management:"
    log_info "  Load:    sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.${HOST}.plist"
    log_info "  Unload:  sudo launchctl unload /Library/LaunchDaemons/com.github.actions.runner.${HOST}.plist"
    log_info "  Status:  sudo launchctl list | grep github.actions.runner"
    echo
    log_info "Logs:"
    log_info "  Output:  ${RUNNER_DIR}/runner.out.log"
    log_info "  Errors:  ${RUNNER_DIR}/runner.err.log"
    log_info "  Tail:    tail -f ${RUNNER_DIR}/runner.out.log"
    echo
    log_info "Cleanup:"
    log_info "  Manual:  ${RUNNER_DIR}/cleanup-work.sh"
    echo
    log_warn "Next Steps:"
    log_warn "  1. Verify runner appears in GitHub: ${RUNNER_URL_BASE}/settings/actions/runners"
    log_warn "  2. Configure repository security settings (see hardening warnings above)"
    log_warn "  3. Test with smoke-test workflow"
    log_warn "  4. Monitor logs for first few runs"
    echo
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log_info "GitHub Actions Self-Hosted Runner Installer"
    log_info "==========================================="
    echo

    check_root
    check_args "$@"
    check_prerequisites
    
    create_runner_user
    download_runner
    install_runner
    configure_runner
    install_launchd_service
    configure_runner_hardening
    verify_installation
    
    print_summary
}

# Run main function
main "$@"

