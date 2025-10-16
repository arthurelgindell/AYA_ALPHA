# GitHub Actions Self-Hosted Runners for ALPHA & BETA
## Mac Studio M3 Ultra (macOS ARM64)

**Status**: Production-Ready  
**Version**: 1.0  
**Date**: October 16, 2025  
**Runner Version**: 2.325.0

---

## Overview

This repository contains configuration and scripts for deploying GitHub Actions self-hosted runners on two Mac Studio M3 Ultra systems (ALPHA and BETA) running macOS ARM64.

### Features

- ✅ Dedicated non-admin `runner` user
- ✅ launchd service for auto-start at boot
- ✅ Unique labels per host for job targeting
- ✅ Security hardening (repository restrictions, token permissions)
- ✅ Periodic work directory cleanup
- ✅ Comprehensive smoke-test workflow
- ✅ Optional local testing with `nektos/act`

---

## Architecture

```
GitHub Organization/Repository
│
├─ Runner: alpha-m3-ultra
│  ├─ Labels: [self-hosted, macOS, arm64, alpha, studio]
│  ├─ System: Mac Studio M3 Ultra (192GB RAM, 4TB SSD)
│  └─ Service: com.github.actions.runner.alpha
│
└─ Runner: beta-m3-ultra
   ├─ Labels: [self-hosted, macOS, arm64, beta, studio]
   ├─ System: Mac Studio M3 Ultra (192GB RAM, 4TB + 16TB SSD)
   └─ Service: com.github.actions.runner.beta
```

---

## Prerequisites

### System Requirements
- macOS Sequoia 15.0 or later
- ARM64 architecture (Apple Silicon)
- Xcode Command Line Tools installed
- Network connectivity to github.com
- Root/sudo access for installation

### GitHub Requirements
- GitHub organization or repository access
- Personal Access Token (PAT) with:
  - `admin:org` scope (for organization runners)
  - `repo` scope (for repository runners)

### Verify Prerequisites

```bash
# Check architecture
uname -m  # Should output: arm64

# Check Xcode CLT
xcode-select -p  # Should output: /Library/Developer/CommandLineTools

# Check network
ping -c 1 github.com  # Should succeed
```

---

## Installation

### 1. Prepare Installation Files

```bash
# Clone or copy files to target system
cd /Users/arthurdell/AYA/github-runners

# Make installer executable
chmod +x install-runner.sh
```

### 2. Install on ALPHA

```bash
# Replace with your actual values
GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
ORG_NAME="your-org-name"
REPO_NAME="your-repo-name"  # Optional, omit for org-wide runner

# Run installer
sudo ./install-runner.sh alpha "$GITHUB_TOKEN" "$ORG_NAME" "$REPO_NAME"
```

### 3. Install on BETA

```bash
# SSH to BETA or run locally
ssh arthurdell@beta.local

# Run installer
sudo ./install-runner.sh beta "$GITHUB_TOKEN" "$ORG_NAME" "$REPO_NAME"
```

### 4. Verify Installation

```bash
# Check service status
sudo launchctl list | grep github.actions.runner

# View logs
tail -f ~/actions-runner/runner.out.log

# Verify in GitHub UI
# Navigate to: https://github.com/ORG_NAME/settings/actions/runners
# (or https://github.com/ORG_NAME/REPO_NAME/settings/actions/runners)
```

---

## Configuration

### Runner Labels

Runners are registered with unique labels for job targeting:

**ALPHA**:
- `self-hosted`
- `macOS`
- `arm64`
- `alpha`
- `studio`

**BETA**:
- `self-hosted`
- `macOS`
- `arm64`
- `beta`
- `studio`

### Workflow Example

```yaml
jobs:
  build:
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    steps:
      - uses: actions/checkout@v4
      - run: make build
```

### Environment Variables

The runner service sets the following environment variables:

```bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/Apple/usr/bin
RUNNER_ALLOW_RUNASROOT=0
RUNNER_NAME=alpha-m3-ultra  # or beta-m3-ultra
```

---

## Security Hardening

### 1. Repository Restrictions

**GitHub UI**: Settings → Actions → Runner groups → Manage runner groups

- ✅ Create dedicated runner group
- ✅ Restrict to selected repositories
- ✅ Add ALPHA and BETA runners to group

### 2. Fork PR Protection

**GitHub UI**: Settings → Actions → General → Fork pull request workflows

- ✅ Disable "Run workflows from fork pull requests"
- ✅ Enable "Require approval for first-time contributors"

### 3. Token Permissions

**GitHub UI**: Settings → Actions → General → Workflow permissions

- ✅ Set to "Read repository contents and packages permissions"
- ✅ Enable "Allow GitHub Actions to create and approve pull requests" (if needed)

### 4. Action Pinning

Always pin actions to specific SHAs:

```yaml
# ❌ BAD: Mutable tag
- uses: actions/checkout@v4

# ✅ GOOD: Pinned to SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
```

### 5. Work Directory Cleanup

The installer creates a cleanup script at `~/actions-runner/cleanup-work.sh`:

```bash
# Manual cleanup
~/actions-runner/cleanup-work.sh

# Or add to cron (runs daily at 2 AM)
crontab -e
0 2 * * * /Users/runner/actions-runner/cleanup-work.sh
```

---

## Service Management

### launchd Commands

```bash
# Load service (start and enable auto-start)
sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.alpha.plist

# Unload service (stop and disable auto-start)
sudo launchctl unload /Library/LaunchDaemons/com.github.actions.runner.alpha.plist

# Check if service is loaded
sudo launchctl list | grep github.actions.runner

# View service details
sudo launchctl print system/com.github.actions.runner.alpha
```

### Logs

```bash
# View output log
tail -f /Users/runner/actions-runner/runner.out.log

# View error log
tail -f /Users/runner/actions-runner/runner.err.log

# View both
tail -f /Users/runner/actions-runner/runner.*.log
```

### Restarting

```bash
# Method 1: Unload and reload
sudo launchctl unload /Library/LaunchDaemons/com.github.actions.runner.alpha.plist
sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.alpha.plist

# Method 2: Reboot system
sudo reboot
```

---

## Testing

### Smoke Test Workflow

Deploy the smoke test workflow to your repository:

```bash
# Copy workflow file to your repository
mkdir -p .github/workflows
cp workflows/runner-smoke.yml .github/workflows/

# Commit and push
git add .github/workflows/runner-smoke.yml
git commit -m "Add runner smoke test"
git push
```

### Run Smoke Test

**GitHub UI**: Actions → Runner Smoke Test → Run workflow

Or trigger via push to the workflow file.

### Expected Output

```
====== System Information ======
OS: macOS 15.0
Architecture: arm64
CPU: Apple M3 Ultra
...

====== Toolchain Validation ======
✅ clang: Apple clang version 15.0.0
✅ xcodebuild: Xcode 15.0
✅ python3: Python 3.11.6
✅ git: git version 2.42.0
...

✅ ALPHA Runner Operational
```

### Local Testing with act

Install `nektos/act`:

```bash
brew install act
```

Test workflow locally:

```bash
# Dry-run
act -n

# Run workflow
act workflow_dispatch -W .github/workflows/runner-smoke.yml

# List workflows
act -l
```

**Note**: `act` has limited macOS support and will run in a Linux container. Use for syntax validation only.

---

## Troubleshooting

### Runner Not Appearing in GitHub

1. Check service is running:
   ```bash
   sudo launchctl list | grep github.actions.runner
   ```

2. Check logs for errors:
   ```bash
   tail -50 /Users/runner/actions-runner/runner.err.log
   ```

3. Verify registration token is valid:
   ```bash
   # Re-run installer with fresh token
   sudo ./install-runner.sh alpha "$NEW_TOKEN" "$ORG_NAME"
   ```

### Runner Offline After Reboot

1. Verify service is set to auto-start:
   ```bash
   sudo launchctl print system/com.github.actions.runner.alpha | grep RunAtLoad
   # Should output: RunAtLoad = true;
   ```

2. Check service logs:
   ```bash
   tail -50 /Users/runner/actions-runner/runner.out.log
   ```

3. Manually load service:
   ```bash
   sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.alpha.plist
   ```

### Permission Denied Errors

1. Check runner directory ownership:
   ```bash
   ls -la /Users/runner/actions-runner
   # Should be owned by runner:staff
   ```

2. Fix permissions:
   ```bash
   sudo chown -R runner:staff /Users/runner/actions-runner
   sudo chmod -R 755 /Users/runner/actions-runner
   ```

### Workflow Fails with "No runner available"

1. Verify labels match:
   ```yaml
   # Workflow
   runs-on: [self-hosted, macOS, arm64, alpha, studio]
   ```

   ```bash
   # Check runner labels in GitHub UI
   # Or check runner config
   cat /Users/runner/actions-runner/.runner
   ```

2. Ensure runner is online in GitHub UI

3. Check runner is accepting jobs:
   ```bash
   tail -10 /Users/runner/actions-runner/runner.out.log | grep "Listening"
   ```

---

## Maintenance

### Update Runner Version

1. Download new runner version:
   ```bash
   cd /Users/runner/actions-runner
   wget https://github.com/actions/runner/releases/download/v2.326.0/actions-runner-osx-arm64-2.326.0.tar.gz
   ```

2. Stop service:
   ```bash
   sudo launchctl unload /Library/LaunchDaemons/com.github.actions.runner.alpha.plist
   ```

3. Backup configuration:
   ```bash
   cp .runner .runner.backup
   cp .credentials .credentials.backup
   ```

4. Extract new version:
   ```bash
   tar xzf actions-runner-osx-arm64-2.326.0.tar.gz
   ```

5. Restart service:
   ```bash
   sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.alpha.plist
   ```

### Cleanup Old Workflow Runs

```bash
# Manual cleanup (removes runs older than 7 days)
~/actions-runner/cleanup-work.sh

# Or add to crontab
0 2 * * * /Users/runner/actions-runner/cleanup-work.sh
```

### Monitor Disk Usage

```bash
# Check work directory size
du -sh /Users/runner/actions-runner/_work

# Check disk space
df -h
```

---

## Uninstallation

### Remove Runner

```bash
# 1. Stop service
sudo launchctl unload /Library/LaunchDaemons/com.github.actions.runner.alpha.plist

# 2. Remove runner from GitHub
sudo -u runner /Users/runner/actions-runner/config.sh remove --token "$REMOVAL_TOKEN"

# 3. Remove service file
sudo rm /Library/LaunchDaemons/com.github.actions.runner.alpha.plist

# 4. Remove runner directory
sudo rm -rf /Users/runner/actions-runner

# 5. (Optional) Remove runner user
sudo dscl . -delete /Users/runner
sudo rm -rf /Users/runner
```

---

## References

- [GitHub Actions Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [macOS launchd Documentation](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- [nektos/act - Local GitHub Actions Testing](https://github.com/nektos/act)
- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review runner logs: `/Users/runner/actions-runner/runner.*.log`
3. Check GitHub Actions status: https://www.githubstatus.com/
4. Consult GitHub Actions documentation

---

## License

Internal use only. Not for redistribution.

**Version**: 1.0  
**Last Updated**: October 16, 2025

