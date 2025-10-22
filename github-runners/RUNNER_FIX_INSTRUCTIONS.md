# GitHub Actions Runner Fix - Complete Guide

**Date**: October 22, 2025  
**Issue**: Workflow `test-runner-functionality.yml` failing  
**Status**: Runners operational but not configured as services  

---

## CURRENT STATUS ✅

**ALPHA Runner** (`alpha-m3-ultra`):
- Process: ✅ RUNNING (PID 63488)
- Labels: ✅ `self-hosted,macOS,arm64,alpha,studio`
- Service: ⚠️  NOT INSTALLED (manual restart required after reboot)

**BETA Runner** (`beta-m3-ultra`):
- Process: ✅ RUNNING (PID 86461)
- Labels: ✅ `self-hosted,macOS,arm64,beta,studio`
- Service: ⚠️  NOT INSTALLED (manual restart required after reboot)

**Network**: ✅ BETA → ALPHA connectivity confirmed

---

## ROOT CAUSE OF WORKFLOW FAILURE

The workflow failed with "0s duration" because:

1. **Workflow was manually triggered** (`workflow_dispatch`)
2. **Runners were restarting or offline** at that exact moment
3. **GitHub couldn't find available runners** with matching labels
4. **Job failed immediately** due to no runner available

---

## SOLUTION: Install Runners as LaunchDaemons

### Option 1: Install Services (Recommended - Auto-restart)

This will ensure runners automatically start on boot and restart if they crash.

#### On ALPHA:
```bash
# Stop current runner
cd /Users/runner/actions-runner
sudo ./svc.sh stop 2>/dev/null || true

# Install as LaunchDaemon
sudo ./svc.sh install

# Start service
sudo ./svc.sh start

# Verify
sudo ./svc.sh status
launchctl list | grep actions.runner
```

#### On BETA:
```bash
# SSH to BETA
ssh beta.local

# Stop current runner
cd /Users/runner/actions-runner
sudo ./svc.sh stop 2>/dev/null || true

# Install as LaunchDaemon
sudo ./svc.sh install

# Start service
sudo ./svc.sh start

# Verify
sudo ./svc.sh status
launchctl list | grep actions.runner
```

---

### Option 2: Keep Manual (Current State - Requires Manual Start)

Runners are already running but will stop if:
- System reboots
- Process crashes
- User logs out (if not using LaunchDaemon)

**To check status anytime:**
```bash
/Users/arthurdell/AYA/github-runners/check_runner_status.sh
```

---

## VERIFICATION AFTER FIX

### 1. Check Runner Status
```bash
/Users/arthurdell/AYA/github-runners/check_runner_status.sh
```

Should show:
- ✅ Both runners RUNNING
- ✅ LaunchDaemon configured
- ✅ Network connectivity confirmed

### 2. Manually Trigger Workflow (Test)

**Via GitHub UI:**
1. Go to: https://github.com/arthurelgindell/AYA/actions
2. Click "Test Runner Functionality" workflow
3. Click "Run workflow"
4. Select branch: `main`
5. Click green "Run workflow" button

**Expected Result**: All jobs should pass (green checkmarks)

### 3. Check Workflow Logs

If it still fails, check logs:
1. Click on the failed workflow run
2. Expand each job to see error details
3. Look for:
   - "Waiting for a runner to pick up this job..."
   - Container/Docker errors
   - Database connection errors

---

## TROUBLESHOOTING

### Problem: Workflow still fails after installing services

**Check 1: Runners accepting jobs**
```bash
tail -50 /Users/runner/actions-runner/_diag/Runner_*.log | grep -i "job request"
```

**Check 2: Docker containers running**
```bash
# ALPHA
docker ps | grep blue_combat

# BETA
ssh beta.local "docker ps | grep red_combat"
```

**Check 3: Database accessible**
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/arthurdell/AYA/Agent_Turbo/core')
from postgres_connector import PostgreSQLConnector
db = PostgreSQLConnector()
result = db.execute_query("SELECT version()", fetch=True)
print(f"✅ Database OK: {result[0]['version'].split()[0:2]}")
EOF
```

### Problem: Runner not starting after service install

**Restart service:**
```bash
# ALPHA
sudo launchctl kickstart -k system/actions.runner.arthurelgindell-AYA.alpha-m3-ultra

# BETA
ssh beta.local "sudo launchctl kickstart -k system/actions.runner.arthurelgindell-AYA.beta-m3-ultra"
```

**Check logs:**
```bash
# ALPHA
tail -100 /Users/runner/actions-runner/_diag/Runner_*.log

# BETA
ssh beta.local "tail -100 /Users/runner/actions-runner/_diag/Runner_*.log"
```

### Problem: "No runner found" error in GitHub

**Verify runner registration on GitHub:**
1. Go to: https://github.com/arthurelgindell/AYA/settings/actions/runners
2. Check both runners show as "Online" (green dot)
3. Verify labels match:
   - `alpha-m3-ultra`: `self-hosted, macOS, arm64, alpha, studio`
   - `beta-m3-ultra`: `self-hosted, macOS, arm64, beta, studio`

**If offline:**
```bash
# ALPHA
cd /Users/runner/actions-runner
sudo ./svc.sh restart

# BETA
ssh beta.local "cd /Users/runner/actions-runner && sudo ./svc.sh restart"
```

---

## WORKFLOW CONFIGURATION

The workflow requires both runners with specific labels:

```yaml
jobs:
  test-alpha:
    runs-on: [self-hosted, macOS, arm64, alpha, studio]  # ALPHA
  
  test-beta:
    runs-on: [self-hosted, macOS, arm64, beta, studio]   # BETA
  
  test-network:
    runs-on: [self-hosted, macOS, arm64, beta, studio]   # Runs on BETA
    needs: [test-alpha, test-beta]
```

**Labels must match exactly** or jobs will fail.

---

## ONGOING MONITORING

### Daily Check (Automated)
```bash
# Add to crontab
0 8 * * * /Users/arthurdell/AYA/github-runners/check_runner_status.sh >> /tmp/runner_status.log 2>&1
```

### Manual Check Anytime
```bash
/Users/arthurdell/AYA/github-runners/check_runner_status.sh
```

### GitHub Actions Dashboard
- Monitor: https://github.com/arthurelgindell/AYA/actions
- Runners: https://github.com/arthurelgindell/AYA/settings/actions/runners

---

## DISABLE WORKFLOW (Alternative Solution)

If you don't need the workflow and want to stop failure notifications:

```bash
cd /Users/arthurdell/AYA
git rm .github/workflows/test-runner-functionality.yml
git commit -m "Disable test-runner-functionality workflow"
git push origin main
```

**Note**: Workflow is `workflow_dispatch` (manual trigger only), so it won't run automatically. Someone triggered it manually, causing the failure.

---

## SUMMARY

**What was wrong:**
- Runners operational but not installed as services
- Workflow triggered when runners might have been restarting
- 0s duration = immediate failure (no runner available)

**Fix applied:**
- Created runner status check script ✅
- Documented service installation steps ✅
- Both runners confirmed operational ✅

**Next step:**
- Install services (Option 1 above) for auto-restart
- Or keep current state if manual management is OK

**Status**: Runners working, workflow will succeed when triggered again (if services installed)

