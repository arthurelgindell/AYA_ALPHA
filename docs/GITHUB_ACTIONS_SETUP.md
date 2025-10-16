# GitHub Actions Self-Hosted Runner Setup

Complete setup for ALPHA and BETA Mac Studio M3 Ultra runners.

## Overview

This setup provides:
- Two self-hosted runners (ALPHA and BETA)
- Unique labels for job targeting
- Auto-start via launchd
- Security hardening
- Periodic cleanup
- Local workflow testing

## Quick Start

### 1. Generate GitHub Token

Create a Personal Access Token with these scopes:
- `admin:org` (for organization runners)
- OR `repo` (for repository runners)

Go to: GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)

### 2. Run Setup Script

**On ALPHA:**
```bash
cd /Users/arthurdell/GLADIATOR/scripts
sudo ./setup-github-runner.sh ALPHA <github-token> <org-name> <repo-name>
```

**On BETA:**
```bash
cd /Volumes/DATA/GLADIATOR/scripts
sudo ./setup-github-runner.sh BETA <github-token> <org-name> <repo-name>
```

### 3. Verify Installation

Check runner appears in GitHub:
- Organization runners: `https://github.com/organizations/<org>/settings/actions/runners`
- Repository runners: `https://github.com/<org>/<repo>/settings/actions/runners`

### 4. Run Smoke Test

Trigger the smoke test workflow:
```bash
# Via GitHub UI: Actions → Runner Smoke Test → Run workflow
# Or push a commit to .github/workflows/runner-smoke.yml
```

## Runner Labels

Target specific runners in workflows:

**ALPHA Runner:**
```yaml
runs-on: [self-hosted, macOS, arm64, alpha, studio]
```

**BETA Runner:**
```yaml
runs-on: [self-hosted, macOS, arm64, beta, studio]
```

**Any Studio:**
```yaml
runs-on: [self-hosted, macOS, arm64, studio]
```

## Management Commands

All commands run as the `runner` user:

```bash
# Switch to runner user
sudo su - runner

# Start runner
~/actions-runner/start-runner.sh

# Stop runner
~/actions-runner/stop-runner.sh

# Check status
~/actions-runner/status-runner.sh

# View logs
~/actions-runner/view-logs.sh

# Manual cleanup
~/actions-runner/cleanup-work.sh
```

## Service Management (launchctl)

```bash
# Load service (as runner user)
launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist

# Unload service
launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist

# Check if loaded
launchctl list | grep com.github.actions.runner

# View service details
launchctl list com.github.actions.runner
```

## Log Files

- **Output logs**: `~/actions-runner/runner.out.log`
- **Error logs**: `~/actions-runner/runner.err.log`
- **Cleanup logs**: `~/actions-runner/cleanup.out.log`

View logs:
```bash
# Tail output logs
tail -f ~/actions-runner/runner.out.log

# Tail error logs
tail -f ~/actions-runner/runner.err.log

# Last 50 lines
~/actions-runner/view-logs.sh
```

## Security Hardening

### Repository Access

**Configure in GitHub:**
1. Repository Settings → Actions → Runners
2. Use repository-specific runners (not org-wide)
3. Restrict to specific repositories only

### Fork Pull Requests

**Disable fork workflows:**
1. Repository Settings → Actions → General
2. Fork pull request workflows → "Require approval for first-time contributors"
3. Or disable: "Disable workflows from forks"

### Action Pinning

Always pin actions to full commit SHAs:

```yaml
# ❌ Bad - uses mutable tag
- uses: actions/checkout@v4

# ✅ Good - pinned to immutable SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
```

Use Dependabot to keep actions updated:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Token Permissions

Default to read-only, escalate per-job:

```yaml
# Workflow-level: read-only default
permissions:
  contents: read

jobs:
  build:
    runs-on: [self-hosted, macOS, arm64, studio]
    # Job-level: escalate only what's needed
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@<sha>
```

### Workflow Security Checklist

- [ ] Pin all actions to commit SHAs
- [ ] Set default permissions to read-only
- [ ] Disable fork workflows (or require approval)
- [ ] Use repository-specific runners
- [ ] Enable branch protection
- [ ] Require code review
- [ ] Use environment secrets
- [ ] Regular security audits

## Local Workflow Testing

Test workflows before pushing to GitHub:

### Install act

```bash
brew install act
```

### Run Workflow Locally

```bash
cd /Users/arthurdell/GLADIATOR
./scripts/test-workflow-locally.sh .github/workflows/runner-smoke.yml
```

**Note**: `act` uses Docker containers and may not perfectly match the ARM64 macOS environment. Always verify on actual runners.

## Troubleshooting

### Runner Not Appearing in GitHub

1. Check logs: `~/actions-runner/runner.err.log`
2. Verify token has correct permissions
3. Check network connectivity
4. Re-run registration: `./config.sh --url <url> --token <new-token>`

### Service Not Starting

```bash
# Check launchd status
launchctl list | grep com.github.actions.runner

# View system log
log show --predicate 'subsystem == "com.apple.launchd"' --last 1h | grep runner

# Check file permissions
ls -la ~/Library/LaunchAgents/com.github.actions.runner.plist
```

### Runner Offline

```bash
# Check if process is running
ps aux | grep "Runner.Listener"

# Restart service
launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist
launchctl load ~/Library/LaunchAgents/com.github.actions.runner.plist
```

### Disk Space Issues

```bash
# Check work directory size
du -sh ~/actions-runner/_work

# Manual cleanup
~/actions-runner/cleanup-work.sh

# Check cleanup schedule
launchctl list | grep cleanup
```

### Workflow Hangs

1. Check runner status: `~/actions-runner/status-runner.sh`
2. View active jobs in GitHub Actions UI
3. Cancel stuck jobs in GitHub
4. Restart runner if needed

## Maintenance

### Update Runner

```bash
# Stop runner
~/actions-runner/stop-runner.sh

# Download new version
cd ~/actions-runner
curl -o actions-runner-osx-arm64-<version>.tar.gz -L \
  https://github.com/actions/runner/releases/download/v<version>/actions-runner-osx-arm64-<version>.tar.gz

# Extract
tar xzf actions-runner-osx-arm64-<version>.tar.gz

# Restart runner
~/actions-runner/start-runner.sh
```

### Regular Tasks

- **Daily**: Automatic cleanup at 3 AM (via launchd)
- **Weekly**: Check disk usage
- **Monthly**: Review security audit logs
- **Quarterly**: Update runner version

## Uninstall

To completely remove a runner:

```bash
# 1. Stop service
launchctl unload ~/Library/LaunchAgents/com.github.actions.runner.plist

# 2. Remove runner from GitHub
cd ~/actions-runner
./config.sh remove --token <token>

# 3. Remove files
rm -rf ~/actions-runner
rm ~/Library/LaunchAgents/com.github.actions.runner.plist
rm ~/Library/LaunchAgents/com.github.actions.runner.cleanup.plist

# 4. Remove user (optional, as root)
sudo dscl . -delete /Users/runner
sudo rm -rf /Users/runner
```

## Additional Resources

- [GitHub Actions Runner Documentation](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Runner Releases](https://github.com/actions/runner/releases)
- [Security Hardening Guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [nektos/act - Local Testing](https://github.com/nektos/act)

## Support

For issues:
1. Check logs: `~/actions-runner/runner.err.log`
2. Review GitHub Actions documentation
3. Check runner status in GitHub UI
4. Restart runner service

For hardening questions, see: `~/actions-runner/HARDENING.md`
