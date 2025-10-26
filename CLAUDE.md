# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AYA Platform Overview

AYA is a production multi-agent orchestration platform featuring Agent Turbo (core orchestration), PostgreSQL backend (centralized state), distributed computing (ALPHA/BETA Mac Studio nodes), and GitHub Actions CI/CD on self-hosted runners.

**Critical Principle**: This platform enforces strict functional reality - if it doesn't run and produce queryable results, it doesn't exist. All operations use actual PostgreSQL, no mocks, no theatrical wrappers.

## System Architecture

### Core Components

**Agent Turbo** (`/Users/arthurdell/AYA/Agent_Turbo/core/`):
- `agent_launcher.py` - Universal agent initialization point (ALL agents start here)
- `agent_orchestrator.py` - Multi-agent session and task management
- `claude_planner.py` - Claude Code specialized interface (planning/auditing)
- `postgres_connector.py` - Database abstraction with connection pooling (2-10 connections)
- `agent_turbo.py` - Knowledge system with RAM disk caching
- `agent_turbo_gpu.py` - MLX GPU acceleration for Apple Silicon
- `lm_studio_client.py` - Local LLM inference client
- `gamma_ray_cluster.py` - Distributed compute (Ray cluster on ALPHA/BETA)
- `gamma_beta_connector.py` - ALPHA-BETA network coordination
- `gamma_syncthing_manager.py` - File synchronization between nodes

### Hardware Infrastructure

- **ALPHA**: Mac Studio M3 Ultra (512GB RAM, 80 GPU cores)
  - Primary PostgreSQL server (aya_rag database)
  - Blue team training and planner execution
  - IP: 100.106.170.128 (Tailscale)

- **BETA**: Mac Studio M3 Ultra (256GB RAM, 16TB SSD, 80 GPU cores)
  - PostgreSQL replica
  - Red team generation and LLM inference (LM Studio)
  - IP: 100.84.202.68 (Tailscale)

- **AIR**: MacBook Air M4
  - Monitoring and secondary operations

### Database Schema (PostgreSQL aya_rag)

**Infrastructure Tables**:
- `system_nodes` - Hardware specifications and status
- `services` - Running services inventory
- `performance_metrics` - Historical performance data

**Agent Turbo Tables**:
- `agent_sessions` - All agent sessions across platforms (landing_context JSONB field)
- `agent_tasks` - Task definitions, status, dependencies
- `agent_actions` - Complete audit trail of all operations
- `agent_artifacts` - Generated files, models, datasets
- `agent_knowledge` - Searchable knowledge entries

**Project Tables**:
- `gladiator_*` - GLADIATOR cyber defense project state

## Common Development Commands

### Agent Turbo Operations

```bash
# Quick start Agent Turbo on ALPHA
cd /Users/arthurdell/AYA/Agent_Turbo
./QUICK_START.sh

# Initialize agent session (Python)
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_launcher.py

# Verify Agent Turbo system
python3 agent_turbo.py verify

# Get system statistics
python3 agent_turbo.py stats

# Query knowledge base
python3 agent_turbo.py query "your query"

# Add knowledge entry
python3 agent_turbo.py add "your knowledge"
```

### Database Operations

```bash
# Connect to PostgreSQL (ALPHA primary)
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag

# Check active agent sessions
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

# View audit trail
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT action_type, success, executed_at
FROM agent_actions
ORDER BY executed_at DESC
LIMIT 10;"
```

### GitHub Actions (Self-Hosted Runners)

```bash
# Trigger GLADIATOR Reality Check workflow
# Via GitHub UI: https://github.com/arthurelgindell/AYA/actions
# Select "GLADIATOR Reality Check" workflow → Run workflow

# Trigger runner smoke test
# Select "Runner Smoke Test" workflow → Run workflow

# Check runner status locally
# ALPHA: /Users/runner/actions-runner/runner.out.log
# BETA: /Users/runner/actions-runner/runner.out.log
```

### Testing

```bash
# Run Agent Turbo performance tests
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 performance_test.py

# Test distributed connectivity (ALPHA → BETA)
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 gamma_beta_connector.py  # Runs test_all_connections()

# Test embedding service
cd /Users/arthurdell/AYA/services
python3 test_embedding_script.py
```

### Deployment

```bash
# Deploy Agent Turbo updates to ALPHA
cd /Users/arthurdell/AYA/Agent_Turbo/scripts
./deploy_to_alpha.sh

# Start Agent Turbo service on ALPHA
./agent_turbo_startup.sh

# Start Agent Turbo service on BETA
./beta_agent_turbo_startup.sh
```

## Multi-Agent Orchestration Pattern

### Agent Initialization Workflow

**All agents MUST initialize through AgentLauncher** to receive landing context and enable audit trail:

```python
from agent_launcher import launch_claude_planner, AgentLauncher

# 1. Initialize Claude Code as planner
context = launch_claude_planner()
session_id = context['session_id']
planner = context['planner_instance']
landing_context = context['landing_context']  # System state snapshot (JSONB)

# 2. Create delegated task
task_id = planner.create_delegated_task(
    task_description='Implement feature X',
    task_type='implementation',
    assigned_to_role='executor',
    priority=8
)

# 3. Initialize specialized agent for the task
launcher = AgentLauncher()
agent_ctx = launcher.initialize_agent(
    platform='openai',  # or 'gemini', 'mistral', etc.
    role='executor',
    parent_session_id=session_id,
    task_context={'task_id': task_id}
)

# 4. Execute task (send agent_ctx['api_payload'] to API)
# ... agent completes work ...

# 5. Log agent response
launcher.log_agent_response(
    session_id=agent_ctx['session_id'],
    task_id=task_id,
    action_description='Completed implementation',
    agent_output='<agent response>',
    execution_time_ms=5000
)

# 6. Audit task results
planner.audit_task_results(
    task_id=task_id,
    audit_status='approved',
    audit_notes='Implementation verified',
    approved=True
)

# 7. Get session summary
summary = planner.get_planning_session_summary()
```

### Landing Context

Landing context is automatically generated at agent initialization and includes:
- System nodes (ALPHA, BETA, AIR) with hardware specs and status
- Active services inventory
- Knowledge base statistics (documents, chunks)
- Recent agent activity metrics
- Database performance metrics

It is stored in `agent_sessions.landing_context` (JSONB) for complete audit trail.

## GitHub Actions Workflows

### Self-Hosted Runners

**ALPHA Runner**:
- Labels: `[self-hosted, macOS, arm64, alpha, studio]`
- Use for: Blue team training, validation, planner execution
- Example: `runs-on: [self-hosted, macOS, arm64, alpha, studio]`

**BETA Runner**:
- Labels: `[self-hosted, macOS, arm64, beta, studio]`
- Use for: Red team generation, LLM inference, dataset creation
- Example: `runs-on: [self-hosted, macOS, arm64, beta, studio]`

### Workflow Architecture

Workflows follow multi-phase orchestration:

1. **Planning Phase** (ubuntu-latest): Claude Code session initialization
2. **Execution Phase** (self-hosted runners): Task execution on ALPHA/BETA
3. **Validation Phase** (self-hosted runners): Result verification
4. **Summary Phase** (ubuntu-latest): Comprehensive reporting

Example: `.github/workflows/reality-check.yml` - GLADIATOR dataset generation and training pipeline

## Performance Characteristics

**Agent Turbo Benchmarks** (verified via performance_test.py):
- Knowledge Add: <50ms target (actual: 27.9ms)
- Knowledge Query: <100ms target (actual: 2.9ms)
- Landing Context Generation: <100ms target (actual: 27.4ms)
- Session Creation: ~12.9ms
- Task Creation: ~0.5ms

**System Capabilities**:
- GPU Acceleration: 160 cores total (80 per M3 Ultra node)
- Cache Hit Rate: >80% after 10 queries (100GB RAM disk)
- Concurrent Sessions: 10 simultaneous agents (connection pool limit)
- Token Optimization: >80% reduction on repeated operations

## Distributed Computing

### Ray Cluster Configuration

- Head node: ALPHA (100.106.170.128:6380)
- Worker node: BETA (100.84.202.68:6380)
- Resource allocation: 32 CPU cores + 80 GPU cores per node (configurable)
- Memory allocation: 80% of available RAM

Access via `gamma_ray_cluster.py`

### File Synchronization (Syncthing)

Synchronized folders between ALPHA and BETA:
- `/Volumes/DATA/GAMMA/AGENT_TURBO` - Agent Turbo core files
- `/Volumes/DATA/GAMMA/AGENT_RAM` - RAM disk cache (100GB)

API: `http://localhost:8384/rest`

Access via `gamma_syncthing_manager.py`

## Project-Specific Notes

### GLADIATOR Project

**Path**: `/Users/arthurdell/AYA/projects/GLADIATOR/`
**Status**: Phase 0 - Reality Check
**Documentation**: `projects/GLADIATOR/docs/GLADIATOR_MASTER_ARCHITECTURE_v2.4.md`

Weapon-as-a-service cyber defense platform with 3,134 verified attack patterns, red/blue adversarial training, and self-hosted automation.

## Key Architectural Patterns

1. **Single Source of Truth**: All state → PostgreSQL aya_rag (replicated ALPHA → BETA)
2. **Landing Context Propagation**: System state snapshot provided to all agents at initialization
3. **Task Delegation Chains**: Parent-child session relationships with dependency tracking
4. **Complete Audit Trail**: Every action logged to `agent_actions` table
5. **Hardware-Aware Optimization**: MLX GPU acceleration, memory-mapped caching, 100GB RAM disk
6. **Zero Theatrical Code**: All operations use actual database; no mocks, no "would integrate" code

## Integration Points

To integrate new AI agent platforms:

1. Import `AgentLauncher` from `agent_launcher.py`
2. Call `initialize_agent(platform, role, parent_session_id, task_context)`
3. Receive landing context and session ID
4. Execute tasks using platform-specific API
5. Log actions via `log_agent_response()`
6. Complete session and generate summary

All agents are automatically tracked in PostgreSQL with complete audit trail.

## Verification Protocol

Before claiming success on any task:

1. **Component Verification**: Test individual services responding
2. **Dependency Chain Verification**: Map and test all dependencies
3. **Integration Verification**: Test end-to-end user workflows
4. **Failure Impact Verification**: Test failure scenarios and cascades

Never rely solely on test suite results - always test actual system functionality with real data producing real, queryable results.

## Directory Structure Reference

```
AYA/
├── Agent_Turbo/           - Production orchestration system
│   ├── core/              - Core orchestration components
│   ├── config/            - Node configurations (alpha_config.py, beta_config.py)
│   └── scripts/           - 45+ utility scripts
├── .github/workflows/     - CI/CD automation (reality-check, runner-smoke, etc.)
├── Databases/             - Knowledge base crawlers and indexed data
├── models/                - Local LLM models
├── mcp_servers_official/  - Model Context Protocol servers
├── projects/GLADIATOR/    - Cyber defense project
├── services/              - Supporting services (embedding, performance tests)
└── aya_schema_implementation.sql - Complete database schema
```

---

**System Status**: OPERATIONAL
**Database**: PostgreSQL 18.0 aya_rag (replicated)
**Runners**: ALPHA ✅ | BETA ✅
**Performance**: All benchmarks PASS
