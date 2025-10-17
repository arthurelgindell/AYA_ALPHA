# BETA GitHub Actions Runner Setup - Complete Prompt for Cursor

**Copy this entire prompt to Cursor on BETA system**

---

## CONTEXT

You are setting up a GitHub Actions self-hosted runner on BETA (Mac Studio M3 Ultra, macOS ARM64).

**System**: BETA (beta.tail5f2bae.ts.net)  
**Hardware**: Mac Studio M3 Ultra, 512GB RAM, 16TB Thunderbolt SSD  
**GitHub Repository**: arthurelgindell/AYA  
**Branch**: gladiator  
**Runner Name**: beta-m3-ultra  
**Labels**: self-hosted, macOS, arm64, beta, studio

---

## CRITICAL INFORMATION

### BETA Directory Structure
```
/Volumes/DATA/GLADIATOR/              ← ACTUAL GLADIATOR project (53GB)
├── attack_patterns/iteration_001/    ← 3,872 attack pattern files
├── armed_exploits/
├── Qwen/Qwen3-14B-MLX-4bit/
└── scripts/

/Users/arthurdell/GLADIATOR/          ← GitHub repo clone location
└── runners/                          ← Runner installation files
    ├── install-runner.sh
    └── launchd/com.github.actions.runner.beta.plist

Docker: red_combat (maps /Volumes/DATA/GLADIATOR → /gladiator/data)
```

### Registration Token
```
BTSYEDFALAGUNNZETIG5TCLI6EZXY
```

**IMPORTANT**: Use `/Volumes/DATA/GLADIATOR/` for actual project data, NOT `/Users/arthurdell/GLADIATOR/`

---

## TASK

Install and configure GitHub Actions self-hosted runner on BETA with these requirements:

1. **Runner Configuration**:
   - Name: `beta-m3-ultra`
   - Labels: `self-hosted,macOS,arm64,beta,studio`
   - Repository: `https://github.com/arthurelgindell/AYA`
   - Registration token: `BTSYEDFALAGUNNZETIG5TCLI6EZXY`
   - User: `runner` (dedicated non-admin user)
   - Directory: `/Users/runner/actions-runner`
   - Version: 2.329.0 (macOS ARM64)

2. **launchd Service**:
   - Service name: `com.github.actions.runner.beta`
   - Auto-start on boot: Yes
   - Logs: `/Users/runner/actions-runner/runner.out.log` and `runner.err.log`
   - Keep alive: Yes (restart on failure)

3. **Verification Requirements** (Prime Directive):
   - ✅ Runner appears in GitHub UI: https://github.com/arthurelgindell/AYA/settings/actions/runners
   - ✅ Service running: `sudo launchctl list | grep github.actions.runner.beta`
   - ✅ Logs show: "Listening for Jobs"
   - ✅ Smoke test passes (if triggered)

4. **Security**:
   - Non-admin `runner` user
   - No sudo access for runner
   - Work directory: `/Users/runner/actions-runner/_work`

---

## FILES AVAILABLE

The runner installer is already on BETA at:
```
/Users/arthurdell/GLADIATOR/runners/install-runner.sh
/Users/arthurdell/GLADIATOR/runners/launchd/com.github.actions.runner.beta.plist
```

---

## INSTALLATION STEPS

### 1. Verify Prerequisites
```bash
# Check architecture
uname -m  # Should be: arm64

# Check Xcode CLT
xcode-select -p  # Should exist

# Check GitHub CLI (optional for runner, but useful)
gh --version || /opt/homebrew/bin/gh --version
```

### 2. Run Installer
```bash
cd /Users/arthurdell/GLADIATOR/runners

arch -arm64 sudo ./install-runner.sh beta "BTSYEDFALAGUNNZETIG5TCLI6EZXY" "arthurelgindell" "AYA"
```

**Expected Output**:
```
✅ User 'runner' created
✅ Runner downloaded (v2.329.0)
✅ Runner installed to /Users/runner/actions-runner
✅ Runner configured successfully
✅ launchd service installed and loaded
```

### 3. Verify Installation
```bash
# Check service is running
sudo launchctl list | grep github.actions.runner.beta
# Should show: PID and service name

# Check logs
sudo tail -20 /Users/runner/actions-runner/runner.out.log
# Should show: "Listening for Jobs"

# Check in GitHub UI
# Navigate to: https://github.com/arthurelgindell/AYA/settings/actions/runners
# Should see: beta-m3-ultra (Idle) with green status
```

---

## VERIFICATION CHECKLIST

Before reporting success, verify:

- [ ] User `runner` exists: `id runner`
- [ ] Runner directory exists: `ls -la /Users/runner/actions-runner`
- [ ] Service loaded: `sudo launchctl list | grep github.actions.runner.beta`
- [ ] Process running: Check PID is not 0
- [ ] Logs show "Listening for Jobs": `sudo tail -5 /Users/runner/actions-runner/runner.out.log`
- [ ] GitHub UI shows runner as "Idle" (green)
- [ ] Labels correct: `[self-hosted, macOS, arm64, beta, studio]`

**Prime Directive**: Do NOT report success unless ALL items above are verified with evidence.

---

## TROUBLESHOOTING

### If installer fails:
```bash
# Check logs
cat /tmp/runner-install.log

# Verify token still valid (expires in 1 hour)
# If expired, get new token from GitHub UI → Settings → Actions → Runners

# Clean up and retry
sudo rm -rf /Users/runner/actions-runner
sudo dscl . -delete /Users/runner
# Then re-run installer
```

### If service won't start:
```bash
# Check plist syntax
plutil -lint /Library/LaunchDaemons/com.github.actions.runner.beta.plist

# Check permissions
ls -la /Library/LaunchDaemons/com.github.actions.runner.beta.plist
# Should be: root:wheel, 644

# Manual load
sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.beta.plist
```

### If runner not appearing in GitHub:
```bash
# Check logs for errors
sudo tail -50 /Users/runner/actions-runner/runner.err.log

# Verify network connectivity
ping -c 3 github.com

# Check runner config
cat /Users/runner/actions-runner/.runner
```

---

## SUCCESS CRITERIA

Report success ONLY when you can provide evidence:

```
✅ BETA RUNNER INSTALLED AND VERIFIED

Evidence:
├─ Service running: com.github.actions.runner.beta (PID: XXXXX)
├─ Log output: "Listening for Jobs" (timestamp: YYYY-MM-DD HH:MM:SS)
├─ GitHub UI: beta-m3-ultra shows "Idle" status
├─ Labels: [self-hosted, macOS, arm64, beta, studio]
└─ Smoke test: [Will be triggered from ALPHA]

File locations:
├─ Runner: /Users/runner/actions-runner/
├─ Logs: /Users/runner/actions-runner/runner.out.log
├─ Service: /Library/LaunchDaemons/com.github.actions.runner.beta.plist
└─ Config: /Users/runner/actions-runner/.runner

Next: Smoke test will be triggered from GitHub to verify runner works
```

---

## AFTER INSTALLATION

Once runner is verified, report back to ALPHA with:
1. Service PID
2. Last 5 lines of runner.out.log
3. Screenshot or confirmation of GitHub UI showing runner as "Idle"

Then ALPHA will trigger smoke test to verify complete workflow.

---

## ADDITIONAL CONTEXT

**Why this runner?**
- BETA is the Red Team system (attack pattern generation)
- Workflows will trigger jobs on BETA for dataset generation
- BETA has 3,134 attack patterns at /Volumes/DATA/GLADIATOR/attack_patterns/
- Docker container `red_combat` mounts this data at /gladiator/data/

**What happens after?**
- Smoke test workflow runs on both ALPHA and BETA
- Reality Check workflow generates 1,000-sample dataset
- Dataset transfers from BETA to ALPHA for training
- Complete audit trail logged to aya_rag database

---

**EXECUTE THE INSTALLATION NOW**

Use the installation command above, verify with the checklist, and report results with evidence.

**Prime Directive**: Verify everything, assume nothing, report facts only.

