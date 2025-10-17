# GLADIATOR Repository Setup Instructions

**Date**: October 16, 2025  
**Status**: Ready to Push

---

## What Has Been Done

✅ Local repository initialized at `/Users/arthurdell/GLADIATOR`  
✅ Complete directory structure created  
✅ Documentation copied (v2.4 architecture, execution plan, test plan)  
✅ Workflows configured (Reality Check, Health Check, Smoke Test)  
✅ Runner configs prepared (ALPHA, BETA launchd plists)  
✅ .gitignore configured (models, datasets, logs excluded)  
✅ README.md created (comprehensive overview)  
✅ LICENSE added (internal use)  
✅ Initial commit prepared

---

## Next Steps

### 1. Create GitHub Repository

**Option A: Via GitHub CLI** (if installed):
```bash
cd /Users/arthurdell/GLADIATOR
gh repo create arthurdell/GLADIATOR --private --source=. --remote=origin --push
```

**Option B: Via GitHub Web UI**:
1. Go to https://github.com/new
2. Repository name: `GLADIATOR`
3. Description: "GLADIATOR Cyber Defense Platform - Adversarial Training"
4. Visibility: **Private** ✅
5. Do NOT initialize with README (we already have one)
6. Click "Create repository"

Then push:
```bash
cd /Users/arthurdell/GLADIATOR
git remote add origin git@github.com:arthurdell/GLADIATOR.git
# or https://github.com/arthurdell/GLADIATOR.git
git push -u origin main
```

---

### 2. Configure Repository Settings

**GitHub UI → GLADIATOR Repository → Settings**

#### A. General
- ✅ Default branch: `main`
- ✅ Allow squash merging
- ✅ Automatically delete head branches

#### B. Actions → General
- ✅ Actions permissions: "Allow all actions and reusable workflows"
- ✅ Workflow permissions: "Read repository contents and packages permissions"
- ✅ Allow GitHub Actions to create and approve pull requests: Optional

#### C. Actions → Runners
**Add Self-Hosted Runners**:

1. Click "New self-hosted runner"
2. Select: macOS, ARM64
3. Copy registration token
4. On ALPHA:
   ```bash
   cd /Users/arthurdell/GLADIATOR/runners
   sudo ./install-runner.sh alpha "YOUR_TOKEN" "arthurdell" "GLADIATOR"
   ```
5. On BETA:
   ```bash
   ssh beta.local
   cd /Users/arthurdell/GLADIATOR/runners
   sudo ./install-runner.sh beta "YOUR_TOKEN" "arthurdell" "GLADIATOR"
   ```
6. Verify both runners show as "Idle" (green) in GitHub UI

#### D. Secrets and Variables → Actions

**Secrets** (if needed):
```
POSTGRES_PASSWORD=<your_aya_rag_password>
```

**Variables**:
```
POSTGRES_HOST=localhost
POSTGRES_DB=aya_rag
POSTGRES_USER=arthur
```

#### E. Branches (Optional Protection)
- Branch name pattern: `main`
- ✅ Require a pull request before merging (optional)
- ✅ Require status checks to pass before merging (optional)

---

### 3. Test Workflows

#### A. Smoke Test (Verify Runners)
1. Go to Actions tab
2. Select "Runner Smoke Test"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

**Expected Result**: Both ALPHA and BETA jobs complete successfully ✅

#### B. Reality Check (Full Pipeline Test)
1. Go to Actions tab
2. Select "GLADIATOR Reality Check"
3. Click "Run workflow"
4. Enter sample size: `1000`
5. Click "Run workflow"

**Expected Result**: 
- Generate Dataset (BETA): ✅
- Transfer (BETA→ALPHA): ✅
- Prepare Training (ALPHA): ✅
- Summary: ✅

---

### 4. Monitor Execution

**GitHub Actions UI**:
- Real-time logs for each step
- Artifacts (if any)
- Workflow run history

**Database** (aya_rag):
```sql
-- Check recent sessions
SELECT * FROM agent_sessions 
ORDER BY start_time DESC 
LIMIT 5;

-- Check GLADIATOR tasks
SELECT * FROM gladiator_execution_plan 
WHERE status = 'pending' 
ORDER BY week_number, day_number;
```

**Runner Logs** (if needed):
```bash
# ALPHA
tail -f /Users/runner/actions-runner/runner.out.log

# BETA
ssh beta.local "tail -f /Users/runner/actions-runner/runner.out.log"
```

---

### 5. Verify Integration

#### Check Runner Status:
```bash
# On ALPHA
sudo launchctl list | grep github.actions.runner

# On BETA
ssh beta.local "sudo launchctl list | grep github.actions.runner"
```

#### Check Database Connectivity:
```bash
psql aya_rag -c "SELECT current_database(), COUNT(*) as session_count FROM agent_sessions"
```

#### Check Docker Containers:
```bash
# ALPHA
docker ps | grep blue_combat

# BETA
ssh beta.local "docker ps | grep red_combat"
```

---

## Repository Structure Overview

```
GLADIATOR/
├── .github/
│   └── workflows/
│       ├── reality-check.yml       ← Main workflow
│       └── runner-smoke.yml        ← Test runners
│
├── docs/
│   ├── GLADIATOR_MASTER_ARCHITECTURE_v2.4.md
│   ├── GLADIATOR_EXECUTION_PLAN_v2.3.md
│   ├── GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.3.md
│   ├── GLADIATOR_MISSION_BRIEFING.md
│   ├── WORKFLOW_SUMMARY.md
│   └── AGENT_TURBO_INTEGRATION.md
│
├── runners/
│   ├── install-runner.sh           ← Use this for setup
│   ├── launchd/
│   │   ├── com.github.actions.runner.alpha.plist
│   │   └── com.github.actions.runner.beta.plist
│   └── README.md
│
├── config/
│   ├── alpha/                      ← ALPHA configs (future)
│   └── beta/                       ← BETA configs (future)
│
├── docker/
│   ├── blue_combat/                ← Blue Team container (future)
│   └── red_combat/                 ← Red Team container (future)
│
├── scripts/                        ← Training scripts (future)
├── models/                         ← .gitignore'd (too large)
├── datasets/                       ← .gitignore'd (too large)
│
├── .gitignore
├── README.md
├── LICENSE
└── SETUP_INSTRUCTIONS.md           ← This file
```

---

## Troubleshooting

### Runner Not Appearing in GitHub
**Check**:
1. Registration token still valid (expires in 1 hour)
2. Service running: `sudo launchctl list | grep github.actions.runner`
3. Logs: `tail -50 /Users/runner/actions-runner/runner.err.log`

**Fix**:
```bash
# Get new token from GitHub UI → Settings → Actions → Runners → New runner
sudo ./install-runner.sh alpha "NEW_TOKEN" "arthurdell" "GLADIATOR"
```

### Workflow Not Triggering
**Check**:
1. Runners online (GitHub UI → Settings → Actions → Runners)
2. Labels match workflow `runs-on: [self-hosted, macOS, arm64, alpha, studio]`
3. Workflow file syntax (Actions tab will show errors)

### Database Connection Failed
**Check**:
1. PostgreSQL running: `brew services list | grep postgresql`
2. Database exists: `psql -l | grep aya_rag`
3. Agent Turbo tables: `psql aya_rag -c "\dt agent_*"`

**Fix**:
```bash
brew services restart postgresql@18
```

---

## What's Next

After setup complete:

1. ✅ **Week 0**: Execute Reality Check (Tasks 1-6)
2. ✅ **Week 1-4**: Pattern expansion + Blue Team training
3. ✅ **Week 5-7**: Knowledge distillation
4. ✅ **Week 8**: Production validation
5. 🎯 **December 11, 2025**: Production Ready

---

## Support

**Documentation**: `docs/` directory  
**Workflow Issues**: GitHub Actions tab → Failed run → Check logs  
**Runner Issues**: `/Users/runner/actions-runner/runner.*.log`  
**Database Issues**: `psql aya_rag` → check `agent_sessions` table

**Contact**: Arthur (arthur@dellight.ai)

---

**Status**: Repository ready to push  
**Next Action**: Create GitHub repo and push  
**Command**: `gh repo create arthurdell/GLADIATOR --private --source=. --remote=origin --push`

