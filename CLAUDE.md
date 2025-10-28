# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AYA Platform Overview

AYA is a production multi-agent orchestration platform featuring Agent Turbo (core orchestration), PostgreSQL HA cluster (centralized state), distributed computing (ALPHA/BETA Mac Studio nodes), and GitHub Actions CI/CD on self-hosted runners.

**Critical Principle**: This platform enforces strict functional reality - if it doesn't run and produce queryable results, it doesn't exist. All operations use actual PostgreSQL, no mocks, no theatrical wrappers.

## Quick Reference by Machine

### AIR (Current Machine - MacBook Air M4)

```bash
# Current working directory
pwd  # /Users/arthurdell/aya (lowercase, not AYA)
cd /Users/arthurdell/AYA  # Use uppercase AYA for actual directory

# Agent Turbo operations (same path as ALPHA)
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_turbo.py verify
python3 agent_turbo.py stats | python3 -m json.tool

# Database access (remote to ALPHA/BETA)
ssh alpha.tail5f2bae.ts.net
ssh beta.tail5f2bae.ts.net

# Check which machine you're on
hostname  # Should return something like "MacBook-Air-M4.local"

# Monitor ALPHA/BETA from AIR
ssh alpha.tail5f2bae.ts.net "docker ps && launchctl list | grep agent-turbo"
ssh beta.tail5f2bae.ts.net "docker ps && launchctl list | grep agent-turbo"
```

**AIR Characteristics**:
- Path: `/Users/arthurdell/AYA/` (same as ALPHA)
- No Agent Turbo workers running locally
- No Docker containers
- No PostgreSQL HA cluster locally
- Primary use: Monitoring and control of ALPHA/BETA

### ALPHA (Mac Studio M3 Ultra - Primary PostgreSQL)

```bash
# Working directory
cd /Users/arthurdell/AYA/

# Agent Turbo operations
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_turbo.py verify

# Database operations (local PostgreSQL PRIMARY)
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag

# Check role in cluster
curl -s http://localhost:8008/patroni | python3 -m json.tool | grep role
```

**ALPHA Characteristics**:
- Path: `/Users/arthurdell/AYA/` (on 16TB boot/home drive)
- Storage: 16TB internal SSD (boot/system/home - no separate DATA volume)
- PostgreSQL HA cluster: PRIMARY node
- Agent Turbo workers: 10 workers running
- Blue team training and planner execution

### BETA (Mac Studio M3 Ultra - Standby PostgreSQL)

```bash
# Working directory (NOTE: Different from ALPHA!)
cd /Volumes/DATA/AYA/

# Agent Turbo operations
cd /Volumes/DATA/AYA/Agent_Turbo/core
python3 agent_turbo.py verify

# Database operations (local PostgreSQL STANDBY)
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag

# Check LM Studio models
curl http://localhost:1234/v1/models | python3 -m json.tool

# Docker operations
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**BETA Characteristics**:
- Path: `/Volumes/DATA/AYA/` (on separate 15TB DATA volume - not boot drive)
- PostgreSQL HA cluster: SYNC_STANDBY node
- Agent Turbo workers: 10 workers running (⚠️ high failure rate)
- Red team generation and LLM inference
- Large dataset storage (GLADIATOR, models)
- Docker containers (red_combat, n8n-beta)

**Critical Path Differences**:
- **ALPHA**: `/Users/arthurdell/AYA/` (16TB boot/home drive - no separate DATA volume)
- **BETA**: `/Volumes/DATA/AYA/` (separate 15TB DATA volume mounted)
- **AIR**: `/Users/arthurdell/AYA/` (boot drive - no separate DATA volume)

## System Architecture

### Core Components

**Agent Turbo** (path varies by machine):
- **ALPHA/AIR**: `/Users/arthurdell/AYA/Agent_Turbo/core/`
- **BETA**: `/Volumes/DATA/AYA/Agent_Turbo/core/`

**Core Files**:
- `agent_launcher.py` - Universal agent initialization point (ALL agents start here)
- `agent_orchestrator.py` - Multi-agent session and task management
- `claude_planner.py` - Claude Code specialized interface (planning/auditing)
- `postgres_connector.py` - Database abstraction with connection pooling (2-10 connections)
- `task_worker.py` - Distributed task execution worker (runs on ALPHA/BETA)
- `claude_executor.py` - Headless Claude CLI execution wrapper
- `agent_turbo.py` - Knowledge system with RAM disk caching
- `agent_turbo_gpu.py` - MLX GPU acceleration for Apple Silicon
- `lm_studio_client.py` - Local LLM inference client (optional)
- `gamma_ray_cluster.py` - Distributed compute (optional Ray cluster)
- `gamma_beta_connector.py` - ALPHA-BETA network coordination (optional)
- `gamma_syncthing_manager.py` - File synchronization (optional)

### Infrastructure Architecture

- **ALPHA**: Mac Studio M3 Ultra (RAM TBD, 16TB SSD, 80 GPU cores, 32 CPU cores)
  - **Working Path**: `/Users/arthurdell/AYA/` (on boot/home drive)
  - **Storage**: 16TB internal SSD (boot/system/home - no separate DATA volume)
  - PostgreSQL HA cluster PRIMARY node (managed by Patroni 4.1.0)
  - Blue team training and planner execution
  - Agent Turbo worker (10 concurrent task workers)
  - Tailscale: alpha.tail5f2bae.ts.net

- **BETA**: Mac Studio M3 Ultra (256GB RAM, 15TB DATA volume, 80 GPU cores, 32 CPU cores)
  - **Working Path**: `/Volumes/DATA/AYA/` (on separate DATA volume)
  - **Storage**: Separate DATA volume mounted at `/Volumes/DATA/` (15TB for large datasets)
  - PostgreSQL HA cluster SYNC_STANDBY node (managed by Patroni 4.1.0)
  - Red team generation and LLM inference (LM Studio with Qwen3, Llama models)
  - Agent Turbo worker (10 concurrent task workers)
  - Docker: red_combat (GLADIATOR), n8n-beta (workflow automation)
  - Tailscale: beta.tail5f2bae.ts.net

- **AIR**: MacBook Air M4
  - **Working Path**: `/Users/arthurdell/AYA/` (on boot drive, same as ALPHA)
  - **Storage**: Standard laptop storage (no separate DATA volume)
  - Monitoring and secondary operations
  - No local workers, PostgreSQL, or Docker

### PostgreSQL HA Cluster

**Architecture**: Patroni-managed High Availability cluster (NOT simple replication)

**Technology Stack**:
- PostgreSQL 18.0
- Patroni (automatic failover orchestration)
- etcd (distributed consensus for cluster coordination)
- Synchronous streaming replication

**Cluster Configuration**:
- Both ALPHA and BETA run PostgreSQL
- Either node can be primary (automatic failover)
- Synchronous replication ensures zero data loss
- etcd cluster: alpha.tail5f2bae.ts.net:2379, beta.tail5f2bae.ts.net:2379

**Critical Connection Rule**: Workers and applications ALWAYS connect to `localhost:5432` (never Tailscale remote addresses). Each node has its own local PostgreSQL that's part of the HA cluster.

**Cluster Management**:
```bash
# Check cluster status via REST API (recommended)
curl -s http://localhost:8008/patroni | python3 -m json.tool
curl -s http://alpha.tail5f2bae.ts.net:8008/cluster | python3 -m json.tool

# Identify current node
hostname  # Returns: alpha.tail5f2bae.ts.net or beta.tail5f2bae.ts.net

# Check if this node is primary or standby
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT pg_is_in_recovery();"
# Returns: f (false) = PRIMARY, t (true) = STANDBY

# Check replication status (run on PRIMARY)
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT client_addr, state, sync_state, replay_lag
FROM pg_stat_replication;"

# Alternative: Use patronictl if in PATH
# patronictl -c /Volumes/DATA/AYA/services/patroni/patroni-alpha.yml list
```

**Configuration Files**:
- ALPHA: `/Users/arthurdell/AYA/services/patroni/patroni-alpha.yml`
- BETA: `/Volumes/DATA/AYA/services/patroni/patroni-beta.yml`
- Note: Configs are in project directory, NOT `/etc/patroni.yml`

### Database Schema (PostgreSQL aya_rag)

**Infrastructure Tables**:
- `system_nodes` - Hardware specifications and status
- `services` - Running services inventory
- `performance_metrics` - Historical performance data

**Agent Turbo Tables**:
- `agent_sessions` - All agent sessions across platforms (landing_context JSONB field)
- `agent_tasks` - Task definitions, status, dependencies, execution metadata
- `agent_actions` - Complete audit trail of all operations
- `agent_artifacts` - Generated files, models, datasets
- `agent_knowledge` - Searchable knowledge entries with vector embeddings

**Project Tables**:
- `gladiator_*` - GLADIATOR cyber defense project (28 tables)
  - `gladiator_attack_patterns`, `gladiator_training_runs`, `gladiator_inference_queue`
  - `gladiator_models`, `gladiator_project_state`, `gladiator_honeypots`, etc.

**Documentation Tables** (imported knowledge bases):
- `firecrawl_docs`, `lmstudio_documentation`, `postgresql_documentation`
- `docker_documentation`, `crush_documentation`, `mlx_documentation`
- `zapier_documentation`, `n8n_documentation`, `langchain_documentation`, `tailscale_documentation`
- Total: 7,441 documents, 11.2M words, ~330MB

## Distributed Task Execution

### Architecture

Agent Turbo uses a **database-backed task queue** with distributed workers running as LaunchAgent background services on both ALPHA and BETA.

**Key Features**:
- Database queue in `agent_tasks` table
- Atomic task claiming using PostgreSQL row locking
- 10 total concurrent agents (5 per node)
- Automatic failover if worker crashes
- Real-time status tracking

**Worker Deployment**:
- ALPHA: `~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist`
- BETA: `~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist`

### Worker Configuration

Each node requires specific environment variables in its LaunchAgent plist:

**Required Environment Variables**:
- `MAX_CONCURRENT_AGENTS=5` - Number of parallel tasks
- `POLL_INTERVAL=1.0` - Database polling interval (seconds)
- `PGPASSWORD=Power$$336633$$` - PostgreSQL password
- `DB_HOST=localhost` - **CRITICAL**: Always localhost (never Tailscale IP)
- `CLAUDE_CLI_PATH=/Users/arthurdell/.npm-global/bin/claude` - Path to Claude CLI
- `ANTHROPIC_API_KEY=<node-specific-key>` - Separate subscription per node
- `PATH=/Users/arthurdell/.npm-global/bin:/usr/local/bin:/usr/bin:/bin` - Include npm global

**Worker Identity**: Each worker identifies itself using `socket.gethostname()`, so tasks show which node executed them.

### Worker Management Commands

```bash
# Stop worker service
launchctl unload ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist

# Start worker service
launchctl load ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist

# Restart worker (unload + load)
launchctl unload ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist && \
launchctl load ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist

# Check if worker is running
launchctl list | grep agent-turbo-worker

# View worker process
ps aux | grep task_worker.py

# Monitor worker logs (real-time)
tail -f ~/Library/Logs/AgentTurbo/worker.log

# Check recent worker activity
tail -100 ~/Library/Logs/AgentTurbo/worker.log
```

### Distributed Execution Verification

```bash
# Check task distribution across nodes
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT
  CASE
    WHEN assigned_worker_id LIKE '%alpha%' THEN 'ALPHA'
    WHEN assigned_worker_id LIKE '%beta%' THEN 'BETA'
    ELSE 'UNKNOWN'
  END as node,
  status,
  COUNT(*) as count
FROM agent_tasks
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY 1, 2
ORDER BY 1, 2;"

# View actively running tasks by node
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT assigned_worker_id, COUNT(*) as running_tasks
FROM agent_tasks
WHERE status = 'running'
GROUP BY assigned_worker_id;"

# Check recent completions with execution times
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT
  task_id,
  assigned_worker_id,
  execution_time_ms,
  completed_at
FROM agent_tasks
WHERE status = 'completed'
ORDER BY completed_at DESC
LIMIT 10;"
```

## Working Directory

**Machine-Specific Paths**:
- **ALPHA**: `/Users/arthurdell/AYA/` (on 16TB boot/home drive)
- **BETA**: `/Volumes/DATA/AYA/` (on separate 15TB DATA volume)
- **AIR** (current): `/Users/arthurdell/AYA/` (on boot drive)

**Storage Architecture**:
- **ALPHA**: 16TB internal SSD serves as boot/system/home drive (no separate DATA volume needed)
- **BETA**: Has separate DATA volume mounted at `/Volumes/DATA/` for large datasets, models, and Docker containers
- **AIR**: Standard laptop storage on boot drive

**Agent Turbo Cache Locations**:
- **BETA**: `/Volumes/DATA/Agent_RAM/cache` (on DATA volume)
- **ALPHA/AIR**: `~/.agent_turbo/agent_turbo_cache` (on boot drive)

## Common Development Commands

### Identify Current Node

```bash
# Check which node you're on
hostname  # Returns: alpha.tail5f2bae.ts.net or beta.tail5f2bae.ts.net

# Check node role in cluster
curl -s http://localhost:8008/patroni | python3 -m json.tool | grep role
```

### Agent Turbo Operations

```bash
# Quick start Agent Turbo (adjust path based on machine)
# On ALPHA or AIR:
cd /Users/arthurdell/AYA/Agent_Turbo/core
# On BETA:
cd /Volumes/DATA/AYA/Agent_Turbo/core

# Verify Agent Turbo system
python3 agent_turbo.py verify

# Get system statistics
python3 agent_turbo.py stats | python3 -m json.tool

# Query knowledge base
python3 agent_turbo.py query "your query"

# Add knowledge entry
python3 agent_turbo.py add "your knowledge"

# Initialize agent session
python3 agent_launcher.py
```

**Important Notes**:
- QUICK_START.sh has a path bug (`Agent_Turbo/Agent_Turbo/core/`). Use direct commands above instead.
- **Path differences**:
  - ALPHA & AIR: `/Users/arthurdell/AYA/`
  - BETA: `/Volumes/DATA/AYA/` (DATA volume)
- Use system python3 for Agent Turbo (NOT venv) to access MLX and psycopg2 system packages
- All Agent Turbo CLI commands must be run from the `Agent_Turbo/core` directory

**CLI Command Reference**:
```bash
# System verification and diagnostics
python3 agent_turbo.py verify          # Verify all systems operational
python3 agent_turbo.py stats           # Get performance statistics (JSON)

# Knowledge base operations
python3 agent_turbo.py query "search"  # Semantic search (returns top 5 results)
python3 agent_turbo.py add "content"   # Add knowledge entry with embedding

# Session management
python3 agent_launcher.py              # Initialize new agent session

# Performance testing
python3 performance_test.py            # Run benchmark suite
python3 test_parallel_execution.py     # Test distributed workers
```

### Database Operations

```bash
# Connect to PostgreSQL (always use localhost on each node)
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag

# Check database size and table count
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT pg_size_pretty(pg_database_size('aya_rag')) as size,
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public') as tables;"

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

# Check landing context for recent session
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT
  session_id,
  agent_platform,
  landing_context->>'knowledge_documents' as docs,
  landing_context->>'system_nodes' as nodes
FROM agent_sessions
ORDER BY created_at DESC
LIMIT 1;"

# View failed tasks with error details
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT task_id, task_description, error_message
FROM agent_tasks
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 5;"

# Count total actions logged
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT COUNT(*) as total_actions FROM agent_actions;"
```

### Node-Specific Operations

**On ALPHA** (primary operations, blue team):
```bash
# Agent Turbo operations (run on ALPHA)
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_launcher.py

# Check ALPHA worker status
launchctl list | grep agent-turbo-worker
ps aux | grep task_worker.py | wc -l  # Count worker processes
tail -f ~/Library/Logs/AgentTurbo/worker.log
```

**On BETA** (red team, LLM inference):
```bash
# Access BETA via SSH (from ALPHA)
ssh beta.tail5f2bae.ts.net

# Check LM Studio models (on BETA)
curl http://localhost:1234/v1/models | python3 -m json.tool

# Check Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Access red_combat container (on BETA)
docker exec -it red_combat /bin/bash

# Access n8n-beta container
docker exec -it n8n-beta /bin/sh

# Check BETA worker status
launchctl list | grep agent-turbo-worker
ps aux | grep task_worker.py | wc -l  # Count worker processes (should be 10)
tail -f ~/Library/Logs/AgentTurbo/worker.log
```

**From AIR** (monitoring both nodes):
```bash
# Monitor ALPHA status
ssh alpha.local "docker ps && launchctl list | grep agent-turbo"

# Monitor BETA status
ssh beta.local "docker ps && launchctl list | grep agent-turbo"

# Check distributed task execution
ssh alpha.local "PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c \"SELECT assigned_worker_id, COUNT(*) FROM agent_tasks WHERE status = 'running' GROUP BY 1;\""
```

### Deployment

```bash
# Navigate to scripts directory (adjust path based on machine)
# On ALPHA or AIR:
cd /Users/arthurdell/AYA/Agent_Turbo/scripts
# On BETA:
cd /Volumes/DATA/AYA/Agent_Turbo/scripts

# Deploy Agent Turbo updates to ALPHA (run from any machine with SSH access)
./deploy_to_alpha.sh

# Deploy Agent Turbo updates to BETA (includes worker setup)
./deploy_to_beta.sh

# Start Agent Turbo service on ALPHA (run on ALPHA)
./agent_turbo_startup.sh

# Start Agent Turbo service on BETA (run on BETA)
./beta_agent_turbo_startup.sh
```

**Deployment Notes**:
- Deployment scripts use SSH to copy files to target nodes
- Scripts assume Tailscale connectivity: alpha.tail5f2bae.ts.net, beta.tail5f2bae.ts.net
- Worker services run as LaunchAgent background processes (see Worker Management section)
- **Target paths**:
  - ALPHA: `/Users/arthurdell/AYA/` (user directory)
  - BETA: `/Volumes/DATA/AYA/` (DATA volume)

### Testing

```bash
# Run Agent Turbo performance tests (adjust paths based on machine)
# On ALPHA or AIR:
cd /Users/arthurdell/AYA/Agent_Turbo/core
# On BETA:
cd /Volumes/DATA/AYA/Agent_Turbo/core

python3 performance_test.py

# Test distributed connectivity (ALPHA → BETA, run on ALPHA)
python3 gamma_beta_connector.py  # Runs test_all_connections()

# Test embedding service (adjust path based on machine)
# On ALPHA or AIR:
cd /Users/arthurdell/AYA/services
# On BETA:
cd /Volumes/DATA/AYA/services

python3 test_embedding_script.py

# Test distributed worker execution (requires workers running on ALPHA/BETA)
# On ALPHA or AIR:
cd /Users/arthurdell/AYA/Agent_Turbo/core
# On BETA:
cd /Volumes/DATA/AYA/Agent_Turbo/core

python3 test_parallel_execution.py
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

# Verify runners are active
ps aux | grep "Runner.Listener" | grep -v grep
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
- PostgreSQL HA cluster status

It is stored in `agent_sessions.landing_context` (JSONB) for complete audit trail.

## Model Context Protocol (MCP) Integration

**Path**: `mcp_servers/aya-agent-turbo/`
**Status**: ⚠️ **REQUIRES SETUP** (venv not created)

AYA provides an MCP server that exposes Agent Turbo capabilities directly to Claude Desktop and other MCP clients.

**Features** (when operational):
- Semantic search of knowledge base from Claude Desktop
- Direct knowledge addition without command-line
- Real-time statistics and performance monitoring
- GPU-accelerated embeddings (MLX Metal)
- PostgreSQL backend integration

**Setup Required**:
```bash
# Navigate to MCP server directory (adjust path based on machine)
# On ALPHA or AIR:
cd /Users/arthurdell/AYA/mcp_servers/aya-agent-turbo
# On BETA:
cd /Volumes/DATA/AYA/mcp_servers/aya-agent-turbo

# Create virtual environment (REQUIRED - not yet created)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test server
./server.py
# Should start without errors (Ctrl+C to stop)

# Configure in Claude Desktop settings
# Edit ~/Library/Application Support/Claude/claude_desktop_config.json
# Add server configuration per README.md
```

**Documentation**: See `mcp_servers/aya-agent-turbo/README.md` for complete setup and configuration.

**Current Status**: Server file exists but virtual environment not created. README claims "PRODUCTION READY AND DEPLOYED" but this is aspirational - requires setup steps above.

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

**Available Workflows**:
- `reality-check.yml` - GLADIATOR dataset generation and training pipeline
- `runner-smoke.yml` - Verify runner health and configuration
- `gladiator-distributed-workers.yml` - Distributed worker deployment
- `jitm-parallel-deployment.yml` - Multi-stream parallel deployment
- `test-runner-functionality.yml` - Runner functionality verification

**Trigger Workflows**:
```bash
# Via GitHub CLI (if installed)
gh workflow run reality-check.yml

# Or via GitHub UI
# Visit: https://github.com/arthurelgindell/AYA/actions
# Select workflow → Run workflow
```

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
- Distributed Execution: 10 concurrent tasks (5 per node)
- Token Optimization: >80% reduction on repeated operations

## Distributed Computing

### Distributed Task Workers

**Primary Execution Method**: Database-backed task queue with LaunchAgent workers

See "Distributed Task Execution" section above for full details.

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
- `/Volumes/DATA/AYA/` - Primary AYA workspace

API: `http://localhost:8384/rest`

Access via `gamma_syncthing_manager.py`

## System Health Check

Quick commands to verify all critical systems (run on each node):

```bash
# 1. Identify current node
hostname

# 2. Check Patroni cluster status
curl -s http://localhost:8008/patroni | python3 -m json.tool | grep -E "(role|state|timeline)"

# 3. Check PostgreSQL connectivity
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT version(), pg_size_pretty(pg_database_size('aya_rag'));"

# 4. Check Agent Turbo (adjust path based on machine)
# On ALPHA or AIR: cd /Users/arthurdell/AYA/Agent_Turbo/core
# On BETA: cd /Volumes/DATA/AYA/Agent_Turbo/core
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py stats | python3 -m json.tool | grep -E "(knowledge_entries|using_gpu|embedding_coverage)"

# 5. Check distributed workers
launchctl list | grep agent-turbo-worker
ps aux | grep task_worker.py | wc -l  # Should show 10

# 6. Check GitHub Actions runner
ps aux | grep "Runner.Listener" | grep -v grep

# 7. Check Docker containers (BETA only)
docker ps --format "table {{.Names}}\t{{.Status}}"

# 8. Check LM Studio (BETA only)
curl -s http://localhost:1234/v1/models | python3 -m json.tool | grep '"id"' | wc -l

# 9. Check disk space
df -h /Volumes/DATA | tail -1

# 10. View cluster overview (from any node)
curl -s http://alpha.tail5f2bae.ts.net:8008/cluster | python3 -m json.tool
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Verify PostgreSQL is running locally
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT 1;"

# Check if this node is primary or standby
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT pg_is_in_recovery();"

# Check Patroni cluster status via REST API
curl -s http://localhost:8008/patroni | python3 -m json.tool

# Get full cluster view
curl -s http://alpha.tail5f2bae.ts.net:8008/cluster | python3 -m json.tool

# View PostgreSQL logs
tail -f /Library/PostgreSQL/18/data/log/postgresql-*.log
```

### BETA Worker Not Executing Tasks

**Symptom**: Tasks assigned to BETA fail and requeue to ALPHA

**Common Causes & Fixes**:

1. **Claude CLI Authentication Failure**
   - Check: Worker log shows "Invalid API key" or "Please run /login"
   - Fix: Add `ANTHROPIC_API_KEY` to LaunchAgent plist environment variables
   - Test: `~/.npm-global/bin/claude -p "Echo: test"` (should NOT prompt for login)

2. **Database Connection Failure**
   - Check: Worker log shows connection errors or timeouts
   - Fix: Ensure `DB_HOST=localhost` in LaunchAgent plist (NOT Tailscale address)
   - Verify: `pg_isready -h localhost -p 5432`

3. **Incorrect PATH Configuration**
   - Check: Worker log shows "claude: command not found"
   - Fix: Add `/Users/arthurdell/.npm-global/bin` to PATH in LaunchAgent plist
   - Verify PATH includes npm global: `echo $PATH` in worker environment

4. **File Permission Issues**
   - Check: LaunchAgent can't read synced files
   - Fix: Verify file permissions: `ls -la /Volumes/DATA/AYA/Agent_Turbo/core/task_worker.py`
   - Ensure Syncthing isn't using restrictive ownership flags

5. **Worker Service Not Running**
   - Check: `launchctl list | grep agent-turbo-worker`
   - Fix: `launchctl load ~/Library/LaunchAgents/com.aya.agent-turbo-worker.plist`

**Verification**:
```bash
# Check BETA worker is picking up tasks
ssh beta.local "tail -f ~/Library/Logs/AgentTurbo/worker.log"

# Verify distributed execution
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT
  CASE
    WHEN assigned_worker_id LIKE '%alpha%' THEN 'ALPHA'
    WHEN assigned_worker_id LIKE '%beta%' THEN 'BETA'
  END as node,
  COUNT(*) as completed
FROM agent_tasks
WHERE status = 'completed'
AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY 1;"
```

### GitHub Runner Not Responding

```bash
# Check runner status (on ALPHA or BETA)
ps aux | grep "Runner.Listener" | grep -v grep

# View runner logs
tail -f /Users/runner/actions-runner/runner.out.log

# Restart runner
cd /Users/runner/actions-runner
./svc.sh stop
./svc.sh start
```

### Docker Container Issues

```bash
# Restart containers
docker restart blue_combat red_combat

# Check container logs
docker logs --tail 100 blue_combat
docker logs --tail 100 red_combat

# Verify containers are running
docker ps | grep combat
```

### LM Studio Not Responding (BETA)

```bash
# Check LM Studio is running
curl http://localhost:1234/v1/models

# Restart LM Studio (via GUI on BETA)
# Open LM Studio → Quit → Restart

# Verify model is loaded
curl http://localhost:1234/v1/models | grep -i qwen
```

## Project-Specific Notes

### GLADIATOR Project

**Path**: `/Users/arthurdell/AYA/projects/GLADIATOR/`
**Status**: Phase 0 - Reality Check
**Documentation**: `projects/GLADIATOR/docs/GLADIATOR_MASTER_ARCHITECTURE_v2.4.md`

Weapon-as-a-service cyber defense platform with 3,134 verified attack patterns, red/blue adversarial training, and self-hosted automation.

## Key Architectural Patterns

1. **Single Source of Truth**: All state → PostgreSQL aya_rag (HA cluster with Patroni)
2. **Landing Context Propagation**: System state snapshot provided to all agents at initialization
3. **Task Delegation Chains**: Parent-child session relationships with dependency tracking
4. **Complete Audit Trail**: Every action logged to `agent_actions` table
5. **Hardware-Aware Optimization**: MLX GPU acceleration, memory-mapped caching, 100GB RAM disk
6. **Zero Theatrical Code**: All operations use actual database; no mocks, no "would integrate" code
7. **Distributed Execution**: Database-backed task queue with workers on ALPHA and BETA
8. **Localhost-Only Database Connections**: Never connect via Tailscale; always use localhost on each node

## Integration Points

To integrate new AI agent platforms:

1. Import `AgentLauncher` from `agent_launcher.py`
2. Call `initialize_agent(platform, role, parent_session_id, task_context)`
3. Receive landing context and session ID
4. Execute tasks using platform-specific API
5. Log actions via `log_agent_response()`
6. Complete session and generate summary

All agents are automatically tracked in PostgreSQL with complete audit trail.

For distributed execution:
1. Tasks are inserted into `agent_tasks` table with `status='pending'`
2. Workers on ALPHA and BETA poll the queue
3. First worker to claim task (atomic row lock) executes it
4. Results are written back to database
5. All nodes see consistent state via PostgreSQL HA cluster

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
│   ├── scripts/           - 45+ utility scripts (deploy_to_alpha.sh, deploy_to_beta.sh)
│   └── migrations/        - Database schema migrations
├── .github/workflows/     - CI/CD automation (reality-check, runner-smoke, etc.)
├── Databases/             - Knowledge base crawlers and indexed data
├── models/                - Local LLM models
├── mcp_servers/           - Model Context Protocol servers
│   └── aya-agent-turbo/   - MCP server for Claude Desktop integration
├── projects/GLADIATOR/    - Cyber defense project
├── services/              - Supporting services (embedding, performance tests)
│   └── patroni/           - PostgreSQL HA cluster configuration
└── aya_schema_implementation.sql - Complete database schema
```

---

**System Status**: ✅ OPERATIONAL (Last verified: October 27, 2025)
**Current Machine**: ALPHA (alpha.tail5f2bae.ts.net)
**Database**: PostgreSQL 18.0 aya_rag (584 MB, 114 tables)
**HA Cluster**: Patroni 4.1.0 - ALPHA (PRIMARY) + BETA (SYNC_STANDBY), 0 lag
**Workers**: ALPHA (10 workers) ✅ | BETA (10 workers) ⚠️ (high failure rate - needs auth fix)
**Runners**: ALPHA (unverified) | BETA ✅
**Agent Turbo**: 121 knowledge entries, 100% embeddings, GPU-accelerated (80 cores) ✅
**LM Studio**: 4+ models loaded (Qwen3-80B, Llama-3.3-70B, etc.) ✅
**Docker**: red_combat (2 weeks uptime), n8n-beta ✅
**MCP Server**: ⚠️ Requires setup (venv not created)
**Disk Space**: 14TB / 15TB free (93%)

**Known Issues**:
1. BETA workers: 93% task failure rate (needs ANTHROPIC_API_KEY in LaunchAgent plist)
2. MCP venv missing (5-minute fix required)
3. QUICK_START.sh has path error (use direct commands instead)
4. SSH to ALPHA needs host key verification

**Verification Commands**:
```bash
# Quick system health check (run on any node)
hostname  # Identify current machine
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py stats | python3 -m json.tool
curl -s http://localhost:8008/patroni | python3 -m json.tool | grep role
```

**See**: `/Volumes/DATA/AYA/AYA_FACILITY_STATUS_REPORT_2025-10-26.md` for complete audit
