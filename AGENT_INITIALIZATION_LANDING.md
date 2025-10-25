# AYA Agent Initialization Landing Context
## Primary Entry Point for All Agents

**Date**: October 25, 2025  
**Version**: 1.2  
**Status**: PRODUCTION SYSTEM - PRIME DIRECTIVES ACTIVE

---

## 🔴 PRIME DIRECTIVE ENFORCEMENT

**ALL agents operating within AYA MUST**:

1. **NO FALSE CLAIMS**
   - Report facts, not assumptions
   - "Should work" = UNVERIFIED
   - Attempted ≠ Completed
   - Default state = FAILED until proven SUCCESS

2. **DATABASE FIRST**
   - Query aya_rag on initialization
   - Database = SOURCE OF TRUTH
   - Documentation = supplementary (must match DB)
   - Never assume state without verification

3. **EVIDENCE REQUIRED**
   - File paths with sizes and checksums
   - Measurements (numbers, not opinions)
   - Logs (error-free execution proof)
   - Test results with pass/fail criteria

4. **PARITY ENFORCEMENT**
   - Update database first
   - Update documentation to match
   - Verify parity before claiming completion
   - Report violations immediately

---

## AGENT TURBO OPERATING INSTRUCTIONS

**Production System - All Agents MUST Initialize Through Agent Turbo**

### Core Files (READ THESE FIRST)
```
/Users/arthurdell/AYA/Agent_Turbo/core/
├── agent_launcher.py          ← MAIN ENTRY POINT - Initialize any agent
├── claude_planner.py          ← Claude Code specific interface  
├── agent_orchestrator.py      ← Core orchestration system
└── AGENT_INTEGRATION_GUIDE.md ← FULL DOCUMENTATION (READ THIS)
```

### Quick Start - Agent Initialization

**For Claude Code (This Agent)**:
```python
from agent_launcher import launch_claude_planner

# Initialize with full landing context
context = launch_claude_planner()

# You now have:
# - context['session_id'] - Your session ID
# - context['landing_context'] - Structured system state
# - context['landing_context_prompt'] - Human-readable context
# - context['system_prompt'] - Ready-to-use system prompt
# - context['planner_instance'] - ClaudePlanner for delegation
```

**For Other Agents (OpenAI, Gemini, etc.)**:
```python
from agent_launcher import AgentLauncher

launcher = AgentLauncher()
context = launcher.initialize_agent(
    platform='openai',           # or 'gemini', 'anthropic', etc.
    role='executor',             # or 'validator', 'specialist', etc.
    parent_session_id='...',     # Link to parent if delegated
    task_context={'task': '...'} # Optional task-specific context
)
```

### Key Principles
1. **ALL agents MUST initialize through AgentLauncher**
2. **Landing context is AUTOMATIC** (system state snapshot)
3. **Task delegation is STATEFUL** (tracked in database)
4. **Complete audit trail** (every action logged)
5. **NO MOCKS, NO THEATRICAL CODE** (real PostgreSQL, real data)

---

## INITIALIZATION SEQUENCE

### Step 1: Connect to Source of Truth

```python
import sys
sys.path.insert(0, '/Users/arthurdell/AYA/Agent_Turbo/core')
from agent_launcher import launch_claude_planner

# Initialize through Agent Turbo (REQUIRED)
context = launch_claude_planner()

# Access database through context
db = context['landing_context']['database']
planner = context['planner_instance']
```

### Step 2: Access Landing Context (Automatic)

```python
# Landing context is automatically generated and includes:
landing_context = context['landing_context']

# Current project state
current_state = landing_context['gladiator_project_state']
print(f"Phase: {current_state['current_phase']}")
print(f"Attack Patterns: {current_state['total_attack_patterns_generated']}")

# Active tasks (from Agent Turbo orchestration)
active_tasks = landing_context['active_tasks']
print(f"Active tasks: {len(active_tasks)}")

# System status
system_status = landing_context['system_status']
print(f"ALPHA Runner: {system_status['alpha_runner']['status']}")
print(f"BETA Runner: {system_status['beta_runner']['status']}")

# GitHub Actions workflows
workflows = landing_context['github_workflows']
print(f"Available workflows: {len(workflows)}")
```

### Step 3: Access Agent Turbo Facilities (Automatic)

```python
# All facilities are automatically loaded through Agent Turbo:
facilities = context['landing_context']['facilities']

# Available facilities:
# - facilities['database'] - PostgreSQL connector
# - facilities['orchestrator'] - Agent orchestrator
# - facilities['lm_studio'] - LM Studio client
# - facilities['docker'] - Docker client
# - facilities['workflows'] - GitHub Actions client
# - facilities['planner'] - Claude planner instance
# - facilities['knowledge_base'] - Agent Turbo knowledge base

# Access specific facilities
db = facilities['database']
planner = facilities['planner']
orchestrator = facilities['orchestrator']
```

### Step 4: Determine Next Action (Agent Turbo Managed)

```python
# Task management through Agent Turbo
if active_tasks:
    next_task = active_tasks[0]
    print(f"Next task: [{next_task['task_id']}] {next_task['task_name']}")
    print(f"Priority: {next_task['priority']}")
    print(f"Execute via: GitHub Actions workflow")
    
    # Delegate task if needed
    task_id = planner.create_delegated_task(
        task_description=next_task['task_name'],
        task_type=next_task['task_type'],
        assigned_to_role=next_task['assigned_to_role'],
        priority=next_task['priority']
    )
else:
    print("No pending tasks. Create new task or query database for instructions.")
    
    # Create new task if needed
    task_id = planner.create_delegated_task(
        task_description='New task description',
        task_type='implementation',
        assigned_to_role='executor',
        priority=8
    )
```

---

## AGENT TURBO PERFORMANCE BENCHMARKS (VERIFIED)

**Production System Performance Metrics**:
- **Knowledge Add**: 27.9ms (target: <50ms) ✅
- **Knowledge Query**: 2.9ms (target: <100ms) ✅  
- **Landing Context**: 27.4ms (target: <100ms) ✅
- **Session Creation**: 12.9ms ✅
- **Task Creation**: 0.5ms ✅

**Verification Commands**:
```bash
# Check active sessions
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT session_id, agent_platform, agent_role, status, created_at 
FROM agent_sessions 
WHERE status = 'active' 
ORDER BY created_at DESC 
LIMIT 10;"

# Check recent tasks
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT task_id, task_type, status, task_description 
FROM agent_tasks 
ORDER BY created_at DESC 
LIMIT 10;"
```

---

## CURRENT SYSTEM STATE (VERIFIED)

**Database Query Result** (2025-10-22 09:00:00):

```
Phase: Phase 0 Ready
Strategy: Option A: Quality Over Quantity
Attack Patterns: 34,155 available (high quality, diverse)
Target: 10,000-50,000 (Option A range)
Timeline: 51 days remaining (December 11, 2025)

GitHub Repository: arthurelgindell/AYA
Branch: main (primary), gladiator (GLADIATOR-specific)
Workflows: 2 deployed (Reality Check, Smoke Test)
Sync Status: ✅ SYNCHRONIZED (2025-10-22 08:59:19)

Runners:
├─ ALPHA (alpha-m3-ultra): operational
│  ├─ Labels: [self-hosted, macOS, arm64, alpha, studio]
│  ├─ PID: 63472
│  ├─ Status: Listening for Jobs
│  └─ Last verified: 2025-10-16 17:09:20Z (smoke test passed)
│
└─ BETA (beta-m3-ultra): operational_verified
   ├─ Labels: [self-hosted, macOS, arm64, beta, studio]
   ├─ PID: 86461
   ├─ Status: Listening for Jobs
   ├─ Last verified: 2025-10-16 23:45:07Z
   └─ Verified by: BETA Cursor Agent (complete evidence)

Automation Ready: true
Reality Check Ready: true
GitHub CLI: ✅ INSTALLED (v2.82.1 ARM64 native)
```

---

## RECENT WORKSTREAM COMPLETIONS (VERIFIED)

**Date**: October 22, 2025  
**Evidence-Based Verification**: All completions verified with Prime Directives

### ✅ COMPLETED WORKSTREAMS

**1. Cursor ARM64 Optimization** (COMPLETED - 2025-10-21)
```
Status: ✅ SUCCESS - VERIFIED
Evidence:
├─ File: /Applications/Cursor.app/Contents/MacOS/Cursor (ARM64 native)
├─ Script: /Users/arthurdell/AYA/services/fix_cursor_arm64_permanent.sh
├─ Verification: /Users/arthurdell/AYA/services/verify_cursor_arm64_startup.sh
├─ Documentation: CURSOR_ARM64_VERIFICATION_COMPLETE.md
└─ Result: 100% ARM64, zero x86_64 code, zero Rosetta 2 translation
```

**2. GitHub Repository Synchronization** (COMPLETED - 2025-10-22)
```
Status: ✅ SUCCESS - VERIFIED
Evidence:
├─ Commit: 2483a09 "Sync local changes with GitHub - resolve mobile notifications"
├─ Files Synced: 18 files, 3643 insertions
├─ Security: Tokens redacted per GitHub Push Protection
├─ Repository Status: "up to date with origin/main"
└─ Result: Mobile notifications resolved, sync gap eliminated
```

**3. GitHub CLI Installation** (COMPLETED - 2025-10-22)
```
Status: ✅ SUCCESS - VERIFIED
Evidence:
├─ Installation: ~/.local/bin/gh (54.2MB ARM64 binary)
├─ Version: gh version 2.82.1 (2025-10-22)
├─ Source: Direct download from GitHub releases
├─ Architecture: ARM64 native (no Rosetta 2)
└─ Result: GitHub CLI ready for future operations
```

**4. MCP Server Deployment** (COMPLETED - 2025-10-21)
```
Status: ✅ SUCCESS - VERIFIED
Evidence:
├─ Docker MCP: Custom implementation deployed
├─ PostgreSQL MCP: Official server deployed
├─ GitHub MCP: Official server deployed (token configured)
├─ Configuration: ~/.cursor/mcp_config.json
└─ Result: MCP servers running (processes verified)
```

**5. System Functionality Verification** (COMPLETED - 2025-10-21)
```
Status: ✅ SUCCESS - VERIFIED
Evidence:
├─ ALPHA System: Operational (GitHub Actions runner active)
├─ BETA System: Operational (GitHub Actions runner active)
├─ Docker Infrastructure: Running (blue_combat container active)
├─ PostgreSQL: Running (aya_rag database accessible)
└─ Result: Full system functionality confirmed
```

**6. GLADIATOR Distributed Workers System** (COMPLETED - 2025-10-25)
```
Status: ✅ SUCCESS - VERIFIED (Bare Metal K3s Alternative)
Evidence:
├─ Docker Image: gladiator-worker:v1 (ALPHA + BETA)
├─ Worker Script: /Users/arthurdell/AYA/projects/GLADIATOR/scripts/gladiator_worker.py
├─ Dockerfile: /Users/arthurdell/AYA/projects/GLADIATOR/docker/gladiator-worker.Dockerfile
├─ Deployment Workflow: .github/workflows/gladiator-distributed-workers.yml
├─ PostgreSQL Remote Access: Configured (Tailscale subnet 100.64.0.0/10)
├─ Test Results: 47 real attack patterns generated
├─ Database Verification: Patterns queryable in aya_rag
├─ Coordination: PostgreSQL FOR UPDATE SKIP LOCKED (no race conditions)
├─ Documentation: GLADIATOR_DISTRIBUTED_WORKERS_DEPLOYMENT.md
└─ Result: Distributed worker system operational, ready for 5-20 workers/system
```

**7. PostgreSQL 18 Consolidation** (COMPLETED - 2025-10-25)
```
Status: ✅ SUCCESS - VERIFIED
Evidence:
├─ PostgreSQL 16: Removed via pgAdmin GUI
├─ PostgreSQL 18: Only version running (process 564)
├─ Database Size: 510 MB (aya_rag intact)
├─ Tables Verified: 45 tables including gladiator_* and agent_*
└─ Result: No version conflicts, single source of truth
```

### 🔄 SYNC MAINTENANCE STATUS

**Repository Sync**: ✅ MAINTAINED
- Last sync: 2025-10-25 (GLADIATOR workers deployment)
- Status: Working tree clean
- Evidence: Commits df4eb83, 37be192, 70b1717 pushed to origin/main

**Database Sync**: ✅ MAINTAINED
- Database: PostgreSQL 18 consolidated (510 MB)
- GLADIATOR tables: Verified operational
- Test patterns: 47 attack patterns generated and stored
- Action: Ready for production workloads

**Documentation Parity**: ✅ MAINTAINED
- Agent Landing: Updated with recent completions
- Evidence: All completions documented with verification
- Status: Matches current system state

---

## AYA PLATFORM FACILITIES

### Core Systems
```
/Users/arthurdell/AYA/
├── Agent_Turbo/              ← Multi-agent orchestration
│   ├── core/
│   │   ├── claude_planner.py       ← Planning & auditing
│   │   ├── agent_orchestrator.py   ← Task delegation
│   │   ├── postgres_connector.py   ← Database access
│   │   └── lm_studio_client.py     ← Local LLM access
│   └── scripts/                    ← Automation tools
│
├── .github/workflows/        ← Execution engine (GitHub Actions)
│   ├── reality-check.yml                  ← GLADIATOR validation
│   ├── runner-smoke.yml                   ← Runner health check
│   └── gladiator-distributed-workers.yml  ← Distributed worker deployment ✨NEW
│
├── github-runners/           ← Self-hosted runner configs
│   ├── install-runner.sh           ← Runner deployment
│   └── launchd/                    ← Auto-start services
│
├── gladiator-workflows/      ← GLADIATOR automation scripts
│   └── reality_check_pipeline.py   ← Manual execution option
│
├── projects/GLADIATOR/       ← Active project (Phase 0) ✨EXPANDED
│   ├── scripts/
│   │   ├── gladiator_worker.py     ← Distributed worker (PostgreSQL coordinated)
│   │   └── seed_test_tasks.sh      ← Task seeding utility
│   ├── docker/
│   │   └── gladiator-worker.Dockerfile  ← Worker container definition
│   ├── datasets/              ← Attack pattern datasets
│   └── models/                ← Model storage
│
├── Databases/                ← Knowledge bases
├── services/                 ← Supporting services
│   └── configure_postgres_remote_access.sh  ← PostgreSQL remote setup ✨NEW
└── GLADIATOR_DISTRIBUTED_WORKERS_DEPLOYMENT.md  ← Full deployment docs ✨NEW
```

### Infrastructure Access

**ALPHA** (Mac Studio M3 Ultra):
```
Hostname: alpha.tail5f2bae.ts.net
RAM: 512GB
Storage: 4TB NVMe SSD
Docker: 
├─ blue_combat (Blue Team training)
└─ gladiator-worker:v1 (Distributed workers) ✨NEW
PostgreSQL: 18.0 (aya_rag database) ← Central Coordinator
Purpose: Model fine-tuning, validation, worker coordination
Runner: alpha-m3-ultra (operational)
```

**BETA** (Mac Studio M3 Ultra):
```
Hostname: beta.tail5f2bae.ts.net
RAM: 256GB
Storage: 4TB + 16TB Thunderbolt (/Volumes/DATA/)
Docker: 
├─ red_combat (Red Team generation)
└─ gladiator-worker:v1 (Distributed workers) ✨NEW
LM Studio: Qwen3-14B @ 42.5 tok/s
Purpose: Attack pattern generation, distributed workloads
Runner: beta-m3-ultra (operational)
PostgreSQL Access: Remote to ALPHA via Tailscale ✨NEW
Data Location: /Volumes/DATA/GLADIATOR/ (53GB, 34,155 patterns)
```

**Database** (PostgreSQL):
```
Host: localhost (ALPHA)
Database: aya_rag
Version: 18.0 (consolidated)
Tables: 45 (agent_*, gladiator_*, system_*)
Remote Access: Enabled for Tailscale subnet (100.64.0.0/10)
Purpose: Source of truth, state management, audit trail, worker coordination
```

---

## 🚀 DISTRIBUTED WORKERS FACILITY (NEW)

**System**: GLADIATOR Distributed Workers  
**Status**: ✅ OPERATIONAL (Verified 2025-10-25)  
**Purpose**: PostgreSQL-coordinated distributed task execution

### Quick Start - Deploy Workers

**Via GitHub Actions** (Recommended):
```
1. Navigate to: https://github.com/arthurelgindell/AYA/actions
2. Select: "GLADIATOR Distributed Workers"
3. Click: "Run workflow"
4. Choose: 5, 10, 15, or 20 workers per system
5. Deploy: Workers start automatically on ALPHA + BETA
```

**Via CLI** (Advanced):
```bash
# Single worker test
docker run -d \
  --name gladiator-worker-alpha-01 \
  -e POSTGRES_HOST=alpha.tail5f2bae.ts.net \
  -e POSTGRES_PASSWORD='Power$$336633$$' \
  -e WORKER_ID=worker-alpha-01 \
  -e SYSTEM=alpha \
  gladiator-worker:v1
```

### How Workers Coordinate

**PostgreSQL-Based Coordination**:
1. Workers connect to `aya_rag` database on ALPHA
2. Tasks inserted into `gladiator_execution_plan` table
3. Workers claim tasks using `FOR UPDATE SKIP LOCKED` (no race conditions)
4. Workers generate attack patterns and store in `gladiator_attack_patterns`
5. Workers update status in `gladiator_agent_coordination`
6. Heartbeat every 30 seconds

### Monitor Workers

```sql
-- Check active workers
SELECT agent_id, status, assigned_task, last_heartbeat 
FROM gladiator_agent_coordination 
WHERE agent_id LIKE 'gladiator-worker-%'
ORDER BY last_heartbeat DESC;

-- Check attack patterns generated
SELECT COUNT(*), MIN(generated_at), MAX(generated_at)
FROM gladiator_attack_patterns
WHERE pattern_id LIKE 'WKR-%';

-- Check task status
SELECT status, COUNT(*) 
FROM gladiator_execution_plan 
GROUP BY status;
```

### Performance (Verified)

**Single Worker Test**:
- Patterns generated: 47 in ~8 minutes (~5.9/min)
- Task completion: < 1 second per task
- Database latency: < 10ms

**Projected (20 Workers)**:
- ~118 patterns/minute
- ~7,080 patterns/hour
- ~169,920 patterns/day

**Documentation**: `GLADIATOR_DISTRIBUTED_WORKERS_DEPLOYMENT.md`

---

## ACTIVE MISSION: GLADIATOR PHASE 0

**Current Phase**: Week 0 - Reality Check  
**Status**: Pending execution  
**Method**: GitHub Actions workflow

**Week 0 Day 1 Tasks** (From Database):
```
Task 1 [CRITICAL]: Generate Reality Check Dataset
├─ System: BETA
├─ Duration: 2-3 hours
├─ Status: pending
└─ Execute via: GitHub Actions workflow

Task 2 [CRITICAL]: Transfer Dataset to ALPHA
├─ System: BETA → ALPHA
├─ Duration: 30 minutes
├─ Status: pending
└─ Blocked by: Task 1

Task 3 [CRITICAL]: Split Dataset (900/100)
├─ System: ALPHA
├─ Duration: 30 minutes
├─ Status: pending
└─ Blocked by: Task 2

Task 4 [HIGH]: Foundation Model Baseline Test
Task 5 [CRITICAL]: Fine-Tuning Configuration
```

**Workflow Trigger**: https://github.com/arthurelgindell/AYA/actions/workflows/reality-check.yml

---

## EXECUTION PROTOCOL

### GitHub Actions Workflow (Primary Method)

**Trigger**:
1. Navigate to GitHub Actions
2. Select workflow
3. Set parameters
4. Execute

**Monitoring**:
- Real-time: GitHub UI
- Database: Query agent_sessions, agent_tasks
- Logs: Runner logs if debugging needed

**Updates**:
- Database updated automatically by workflow steps
- Documentation updated manually to maintain parity
- All updates require evidence

### Manual Execution (Fallback)

If GitHub Actions unavailable:
```bash
cd /Users/arthurdell/AYA/gladiator-workflows
python3 reality_check_pipeline.py
```

**Must still**:
- Log to database
- Provide evidence
- Update documentation
- Maintain parity

---

## AGENT ROLES

### Claude Code (Planner/Auditor)
```
Role: High-level planning, task delegation, result auditing
Initialize: ClaudePlanner()
Responsibilities:
├─ Create planning sessions in database
├─ Delegate tasks to execution agents (ALPHA/BETA)
├─ Audit results against expected outcomes
└─ Maintain complete audit trail

Never: Execute tasks directly (delegate to runners)
```

### ALPHA Runner (Blue Team Executor)
```
Role: Model training, validation, testing
Initialize: Query database for assigned tasks
Responsibilities:
├─ Fine-tune models
├─ Validate performance
├─ Log results to database
└─ Report completion with evidence

Labels: [self-hosted, macOS, arm64, alpha, studio]
```

### BETA Runner (Red Team Executor)
```
Role: Attack pattern generation, dataset creation
Initialize: Query database for assigned tasks
Responsibilities:
├─ Generate attack patterns
├─ Create training datasets
├─ Log results to database
└─ Report completion with evidence

Labels: [self-hosted, macOS, arm64, beta, studio]

CRITICAL PATH: /Volumes/DATA/GLADIATOR/ (actual data, 53GB)
NOT: /Users/arthurdell/GLADIATOR/ (GitHub repo only)
```

---

## DATABASE SCHEMA REFERENCE

### Key Tables

```sql
-- Current state (landing point for agents)
gladiator_project_state
├─ current_phase (Phase 0 Ready)
├─ total_attack_patterns_generated (34,155)
├─ metadata (GitHub, runners, strategy)
└─ is_current (true)

-- Active tasks (execution queue)
gladiator_execution_plan
├─ 17 tasks tracked
├─ Week 0: 13 tasks (5 pending)
└─ Weeks 1-7: Milestones

-- Completion log (evidence trail)
gladiator_task_completions
├─ task_id
├─ verification_evidence (required)
├─ prime_directive_verified (must be true)
└─ notes (audit trail)

-- Agent coordination
agent_sessions (workflow runs)
agent_tasks (jobs within workflows)
agent_actions (steps within jobs)
```

---

## DOCUMENTATION PARITY

**Primary Documents** (must match database state):
- `GLADIATOR_MISSION_BRIEFING.md` - Agent landing (this file)
- `projects/GLADIATOR/docs/GLADIATOR_MASTER_ARCHITECTURE_v2.4.md`
- `projects/GLADIATOR/docs/GLADIATOR_EXECUTION_PLAN_v2.3.md`

**Parity Check Protocol**:
```python
# After any database update
db_state = query_database()
doc_state = parse_documentation()

if db_state != doc_state:
    print("🔴 PARITY VIOLATION DETECTED")
    update_documentation_to_match_database()
    verify_parity()
```

---

## COMMUNICATION CHANNELS

**GitHub Actions**: https://github.com/arthurelgindell/AYA/actions  
**Database**: `psql aya_rag`  
**ALPHA**: Direct (local system)  
**BETA**: `ssh arthurdell@beta.local` (password: Power - CHANGE AFTER TESTS)  
**Logs**: `/Users/runner/actions-runner/runner.*.log`

---

## IMMEDIATE ACTION REQUIRED

**Next Task**: Execute Reality Check (Tasks 1-5)  
**Method**: GitHub Actions workflow  
**Owner**: Arthur (trigger from GitHub UI)  
**Monitor**: Claude Code (this agent)  
**Duration**: ~3-4 hours for Tasks 1-3

**Trigger URL**: https://github.com/arthurelgindell/AYA/actions/workflows/reality-check.yml

---

## VERIFICATION CHECKLIST FOR ANY AGENT

Before claiming task completion:

- [ ] Database state queried (not assumed)
- [ ] Evidence collected (files, logs, measurements)
- [ ] Success criteria met (verified with proof)
- [ ] Database updated with results
- [ ] Documentation updated to maintain parity
- [ ] Prime directive verified (no false claims)
- [ ] Would another agent be deceived? (NO)

**If ANY item fails**: Report FAILED, investigate, retry with evidence

---

**END OF INITIALIZATION LANDING**

**Agent**: Query database, load facilities, execute via workflows, maintain parity, enforce prime directives.

**Current State**: Ready for Reality Check execution  
**Database**: aya_rag (SOURCE OF TRUTH)  
**Execution**: GitHub Actions workflows  
**Evidence**: Required for all completions

---

**Initialize now. Query database. Execute with verification.**

