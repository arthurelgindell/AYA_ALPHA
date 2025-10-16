# GitHub Actions + Agent Turbo: Workflow Summary
## Executive Overview

**Date**: October 16, 2025  
**Integration**: ALPHA/BETA Self-Hosted Runners ↔ Agent Turbo Orchestration  
**Purpose**: Automated GLADIATOR CI/CD with Complete Audit Trail

---

## Quick Start

```bash
# 1. Install runners on ALPHA and BETA
sudo ./install-runner.sh alpha "$GITHUB_TOKEN" "$ORG_NAME"
sudo ./install-runner.sh beta "$GITHUB_TOKEN" "$ORG_NAME"

# 2. Copy workflows to repository
cp github-runners/workflows/*.yml .github/workflows/

# 3. Trigger workflow
# GitHub UI → Actions → GLADIATOR Reality Check → Run workflow
```

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Repository                          │
│               .github/workflows/*.yml                         │
└───────────────────┬──────────────────────────────────────────┘
                    │
       ┌────────────▼──────────┐      ┌──────────────────┐
       │  GitHub Actions       │      │  Claude Code     │
       │  (Trigger/Dispatch)   │◄─────┤  (Planner)       │
       └────────────┬──────────┘      └────────┬─────────┘
                    │                           │
         ┌──────────▼───────────┐               │
         │  Job Router          │               │
         │  (Label Matching)    │               │
         └──────────┬───────────┘               │
                    │                           │
     ┌──────────────┴──────────────┐            │
     │                              │            │
┌────▼────┐                   ┌────▼────┐       │
│  ALPHA  │                   │  BETA   │       │
│ Runner  │                   │ Runner  │       │
│ (Blue   │                   │ (Red    │       │
│  Team)  │                   │  Team)  │       │
└────┬────┘                   └────┬────┘       │
     │                              │            │
     └──────────────┬───────────────┘            │
                    │                            │
              ┌─────▼─────────┐                  │
              │   aya_rag     │◄─────────────────┘
              │   Database    │
              │  (Postgres)   │
              └───────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼────┐           ┌───▼────┐
    │Sessions │           │ Tasks  │
    │(Runs)   │           │(Jobs)  │
    └─────────┘           └────────┘
         │                     │
    ┌────▼────┐           ┌───▼────┐
    │Actions  │           │Artifacts│
    │(Steps)  │           │(Files)  │
    └─────────┘           └─────────┘
```

---

## Key Components

### 1. Self-Hosted Runners

**ALPHA** (Blue Team Training):
- **Purpose**: Model fine-tuning, validation, testing
- **Labels**: `[self-hosted, macOS, arm64, alpha, studio]`
- **Hardware**: Mac Studio M3 Ultra, 192GB RAM, 4TB SSD
- **Docker**: `blue_combat` container
- **Database Role**: Task executor

**BETA** (Red Team Generation):
- **Purpose**: Attack pattern generation, LLM inference
- **Labels**: `[self-hosted, macOS, arm64, beta, studio]`
- **Hardware**: Mac Studio M3 Ultra, 192GB RAM, 16TB SSD
- **Docker**: `red_combat` container
- **Database Role**: Task executor

### 2. Agent Turbo Integration

**Claude Code** (Planner/Auditor):
- Creates planning sessions for workflows
- Delegates tasks to ALPHA/BETA
- Audits results post-execution
- Logs complete audit trail to database

**Database** (aya_rag PostgreSQL):
- `agent_sessions`: Workflow runs
- `agent_tasks`: Jobs within workflows
- `agent_actions`: Steps within jobs
- `agent_artifacts`: Output files, models, datasets

### 3. Workflow Types

**A. GLADIATOR Reality Check**:
- **Trigger**: Manual (workflow_dispatch) or scheduled (daily)
- **Flow**: BETA generates dataset → Transfer to ALPHA → ALPHA fine-tunes → ALPHA validates → GO/NO-GO decision
- **Duration**: ~12-24 hours
- **Output**: Validated model + metrics

**B. Pattern Generation**:
- **Trigger**: Manual with parameters (category, count)
- **Flow**: BETA generates patterns → Commit to repository
- **Duration**: ~1-6 hours (depending on count)
- **Output**: New attack pattern files

**C. Health Check**:
- **Trigger**: Scheduled (daily at 8 AM)
- **Flow**: Check ALPHA and BETA system resources, Docker status, database connectivity
- **Duration**: ~5 minutes
- **Output**: Health report

**D. Smoke Test**:
- **Trigger**: Push to workflow file or manual
- **Flow**: Verify toolchain, cache, network on both runners
- **Duration**: ~2 minutes
- **Output**: Operational status

---

## Workflow Examples

### Example 1: GLADIATOR Reality Check

```yaml
name: GLADIATOR Reality Check

on:
  workflow_dispatch:
    inputs:
      sample_size:
        description: 'Number of patterns'
        default: '1000'

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - name: Initialize Agent Turbo Session
        run: |
          python3 Agent_Turbo/core/claude_planner.py \
            --task "gladiator_reality_check" \
            --context "sample_size=1000"

  generate-dataset:
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    needs: plan
    steps:
      - name: Generate Patterns
        run: |
          docker exec red_combat python3 /gladiator/scripts/generate_dataset.py

  finetune-model:
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    needs: generate-dataset
    steps:
      - name: Fine-tune
        run: |
          docker exec blue_combat python3 /gladiator/scripts/finetune.py

  validate:
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    needs: finetune-model
    steps:
      - name: Validate Model
        run: |
          docker exec blue_combat python3 /gladiator/scripts/validate.py
      
      - name: GO/NO-GO Decision
        run: |
          if [[ $ACCURACY -ge 90 ]]; then
            echo "✅ GO: Proceed to production"
          else
            echo "❌ NO-GO: Debug required"
            exit 1
          fi
```

### Example 2: Daily Health Check

```yaml
name: Daily Health Check

on:
  schedule:
    - cron: '0 8 * * *'

jobs:
  health-alpha:
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    steps:
      - name: System Check
        run: |
          top -l 1 | grep "CPU usage"
          df -h
          docker ps

  health-beta:
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    steps:
      - name: System Check
        run: |
          top -l 1 | grep "CPU usage"
          df -h /Volumes/DATA
          docker ps
```

---

## Database Integration

### Logging Pattern

```python
# 1. Start session (planning phase)
from claude_planner import ClaudePlanner
planner = ClaudePlanner()
session_id = planner.start_planning_session(
    task_type="gladiator_reality_check",
    context={"sample_size": 1000}
)

# 2. Create tasks (planning phase)
task_id = planner.create_delegated_task(
    session_id=session_id,
    task_name="Generate Dataset",
    assigned_agent="BETA"
)

# 3. Log task execution (runner)
orchestrator = AgentOrchestrator()
orchestrator.log_agent_action(
    task_id=task_id,
    action_type="dataset_generation",
    status="started"
)

# 4. Log completion (runner)
orchestrator.update_task_status(
    task_id=task_id,
    status="completed",
    result={"patterns": 1000, "accuracy": 95.2}
)

# 5. Audit results (auditor)
audit = planner.audit_task_results(
    session_id=session_id,
    expected_outcomes={"accuracy": ">=90%"}
)
```

### Query Examples

```sql
-- Get last 10 workflow runs
SELECT 
    session_id,
    github_run_id,
    status,
    start_time,
    end_time
FROM agent_sessions
WHERE context->>'workflow' = 'GLADIATOR Reality Check'
ORDER BY start_time DESC
LIMIT 10;

-- Calculate average accuracy
SELECT AVG((result->>'accuracy')::numeric) as avg_accuracy
FROM agent_tasks
WHERE task_name = 'Validate Model Performance'
  AND status = 'completed';

-- Find failures in last 7 days
SELECT 
    s.github_run_id,
    t.task_name,
    t.assigned_agent,
    a.output
FROM agent_sessions s
JOIN agent_tasks t ON s.session_id = t.session_id
JOIN agent_actions a ON t.task_id = a.task_id
WHERE t.status = 'failed'
  AND s.start_time > NOW() - INTERVAL '7 days';
```

---

## Benefits

| Feature | Benefit |
|---------|---------|
| **Complete Audit Trail** | Every workflow run logged with full context |
| **Claude Code Oversight** | Automated planning, delegation, and auditing |
| **Multi-Agent Orchestration** | ALPHA/BETA coordinated via labels |
| **GLADIATOR Integration** | Automated training/validation pipelines |
| **Developer Experience** | Self-service workflows, automated schedules |
| **Debugging** | Full logs and context for every failure |
| **Performance Tracking** | Historical metrics for optimization |
| **Compliance** | Immutable audit logs for governance |

---

## Security

### Hardening Applied

1. **Repository Restrictions**: Runners limited to specific repos
2. **Fork PR Protection**: Disabled untrusted fork PRs
3. **Token Permissions**: Read-only by default, escalate per-job
4. **Action Pinning**: All actions pinned to specific SHAs
5. **Work Directory Cleanup**: Periodic cleanup between runs
6. **Non-Admin User**: Dedicated `runner` user (no sudo)
7. **launchd Service**: Auto-restart on failure, log rotation

### Example Workflow Security

```yaml
permissions:
  contents: read  # Read-only by default

jobs:
  secure-job:
    runs-on: [self-hosted, macOS, arm64, alpha, studio]
    steps:
      # Pinned to specific SHA
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
      
      # Escalate permissions for this step only
      - name: Push Results
        permissions:
          contents: write
        run: git push origin results
```

---

## Monitoring

### Real-Time (GitHub UI)
- Actions tab: Live workflow progress
- Artifacts: Download outputs
- Logs: Step-by-step execution logs

### Historical (Database)
```sql
-- Dashboard query
SELECT 
    status,
    COUNT(*) as runs,
    AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration_sec,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*), 2) as success_rate_pct
FROM agent_sessions
WHERE context->>'workflow' = 'GLADIATOR Reality Check'
  AND start_time > NOW() - INTERVAL '30 days'
GROUP BY status;
```

### Alerts

```bash
# Add to cron for daily failure report
0 9 * * * psql aya_rag -c "
  SELECT 
    github_run_id,
    task_name,
    output
  FROM agent_sessions s
  JOIN agent_tasks t ON s.session_id = t.session_id
  WHERE t.status = 'failed'
    AND s.start_time > NOW() - INTERVAL '1 day'
" | mail -s 'Failed Workflows' arthur@dellight.ai
```

---

## Troubleshooting

### Runner Not Picking Up Jobs

**Symptoms**: Workflow queued forever

**Checks**:
1. Runner online in GitHub: `Settings → Actions → Runners`
2. Labels match: `runs-on` vs runner labels
3. Service running: `sudo launchctl list | grep github.actions.runner`

**Fix**:
```bash
# Restart runner
sudo launchctl unload /Library/LaunchDaemons/com.github.actions.runner.alpha.plist
sudo launchctl load /Library/LaunchDaemons/com.github.actions.runner.alpha.plist
```

### Database Connection Failures

**Symptoms**: Task logging fails

**Checks**:
1. Postgres running: `pg_isready -h localhost`
2. Network: `ping alpha.local`
3. Credentials in workflow environment variables

**Fix**:
```bash
# Restart Postgres
brew services restart postgresql@18
```

### Workflow Fails Silently

**Symptoms**: No error in GitHub UI, but task incomplete

**Check Database**:
```sql
-- Find last action for task
SELECT 
    action_description,
    status,
    output
FROM agent_actions
WHERE task_id = '<task_id>'
ORDER BY start_time DESC
LIMIT 1;
```

---

## Next Steps

1. **Deploy Runners**: Install on ALPHA and BETA
2. **Copy Workflows**: Add to `.github/workflows/`
3. **Test Smoke**: Run `runner-smoke.yml`
4. **Run Reality Check**: Trigger `gladiator-reality-check.yml`
5. **Monitor**: Check GitHub UI and database logs
6. **Iterate**: Adjust workflows based on results

---

## Files Included

```
github-runners/
├── install-runner.sh                    # Runner installation script
├── launchd/
│   ├── com.github.actions.runner.alpha.plist
│   └── com.github.actions.runner.beta.plist
├── workflows/
│   ├── runner-smoke.yml                 # Smoke test
│   ├── gladiator-reality-check.yml      # Full example
│   ├── gladiator-pattern-generation.yml # Pattern gen
│   └── gladiator-health-check.yml       # Daily health
├── Agent_Turbo/core/
│   └── task_logger.py                   # Database logger
├── AGENT_TURBO_INTEGRATION.md           # Full documentation
├── WORKFLOW_SUMMARY.md                  # This file
└── README.md                            # Runner documentation
```

---

## Support

**Documentation**:
- Agent Turbo: `Agent_Turbo/AGENT_INTEGRATION_GUIDE.md`
- GitHub Actions: https://docs.github.com/en/actions
- Self-Hosted Runners: https://docs.github.com/en/actions/hosting-your-own-runners

**Troubleshooting**:
1. Check runner logs: `/Users/runner/actions-runner/runner.*.log`
2. Check database logs: `SELECT * FROM agent_actions WHERE status = 'failed'`
3. Check GitHub Actions status: https://www.githubstatus.com/

---

**Version**: 1.0  
**Date**: October 16, 2025  
**Status**: Production Ready  
**Integration**: GitHub Actions ↔ Agent Turbo ✅

