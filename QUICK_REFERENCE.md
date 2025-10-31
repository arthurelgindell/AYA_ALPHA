# AYA QUICK REFERENCE CARD
**Session**: claude_code_planner_484911c2 | **Date**: Oct 30, 2025

## 🔴 AYA BULLET PROOF PRIME DIRECTIVES

**MANDATORY COMPLIANCE**: All operations governed by AYA BULLET PROOF PRIME DIRECTIVES

**Master Document**: `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md`

**Key Principles**:
- **Functional Reality Only** (Default = FAILED until proven)
- **Truth Over Comfort** (Report actual state)
- **Bulletproof Verification Protocol** (4-phase verification mandatory)
- **Zero Tolerance for Theatrical Wrappers** (No mocks, no stubs, no fake data)

**Full Reference**: See `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md` for complete governance framework

---

## DATABASE (Source of Truth)
```bash
# Connect
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag

# Quick queries
# Current GLADIATOR state
SELECT current_phase, total_attack_patterns_generated FROM gladiator_project_state WHERE is_current = true;

# Active agents
SELECT COUNT(*) FROM agent_sessions WHERE status = 'active';

# Pending tasks
SELECT task_name, priority FROM gladiator_execution_plan WHERE status = 'pending' ORDER BY priority DESC;
```

## GITHUB ACTIONS
```bash
# Fix PATH first (in each shell)
export PATH="$HOME/.local/bin:$PATH"

# List workflows
gh workflow list

# Trigger Reality Check
gh workflow run reality-check.yml --raw-field sample_size=1000

# Trigger Distributed Workers
gh workflow run gladiator-distributed-workers.yml --raw-field workers_per_system=10

# Check recent runs
gh run list --limit 5

# View run logs
gh run view [RUN_ID] --log
```

## LM STUDIO
```bash
# Check available models
curl http://localhost:1234/v1/models

# Test inference
curl http://localhost:1234/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "foundation-sec-8b-instruct-int8", "prompt": "Test", "max_tokens": 10}'
```

## DOCKER
```bash
# List containers
docker ps

# Access blue_combat
docker exec -it blue_combat /bin/bash

# Check logs
docker logs blue_combat --tail 50

# Deploy workers (from workflow or manual)
docker run -d --name gladiator-worker-01 gladiator-worker:v1
```

## INFRASTRUCTURE
```bash
# Check ALPHA runner
ps aux | grep "Runner.Listener" | grep -v grep

# Database size
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT pg_size_pretty(pg_database_size('aya_rag'));"

# System info
system_profiler SPHardwareDataType | grep -E "(Memory|Processor)"

# Check BETA data (if SSH needed)
ssh arthurdell@beta.local "du -sh /Volumes/DATA/GLADIATOR/ && find /Volumes/DATA/GLADIATOR/attack_patterns -name '*.json' | wc -l"
```

## AGENT TURBO
```python
# Initialize Claude planner
from agent_launcher import launch_claude_planner
context = launch_claude_planner()
session_id = context['session_id']

# Query database
from postgres_connector import PostgreSQLConnector
db = PostgreSQLConnector()
result = db.execute_query("SELECT * FROM gladiator_project_state WHERE is_current = true", fetch=True)
```

## KEY PATHS
- Agent Turbo: `/Users/arthurdell/AYA/Agent_Turbo/core/`
- GLADIATOR Data (BETA): `/Volumes/DATA/GLADIATOR/` (53GB, 34,155 patterns)
- Workflows: `/Users/arthurdell/AYA/.github/workflows/`
- Database Schema: `/Users/arthurdell/AYA/aya_schema_implementation.sql`

## STATUS CHECKS
- Database: 578 MB, 55 tables ✅
- ALPHA Runner: PID 63488 (9+ days) ✅
- Docker: blue_combat (11 days) ✅
- LM Studio: 3+ models loaded ✅
- GLADIATOR: Week 5-8, production phase ✅

## CURRENT FOCUS
**GLADIATOR Week 5-8**: Production deployment with distributed workers
**Timeline**: Oct 24-27, 2025 (ahead of schedule)
**Models**: Binary 99.78%, Multiclass 98.86% (production ready)
**Next**: Deploy 10-20 workers for final dataset expansion
