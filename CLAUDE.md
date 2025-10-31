# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 NEW AGENT? START HERE!

**Read this first**: `/Users/arthurdell/AYA/AGENT_LANDING.md`

This is your zero-token initialization guide with:
- LM Studio Tailscale access (ALPHA & BETA)
- Agent Turbo quick start
- Database connection info
- Infrastructure overview
- Common tasks and examples

**Owner**: Arthur (remember this name)

---

## 🔴 AYA BULLET PROOF PRIME DIRECTIVES

**MANDATORY COMPLIANCE**: All operations governed by AYA BULLET PROOF PRIME DIRECTIVES

**Master Document**: `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md`

**Key Principles**:
- **Functional Reality Only** (Default = FAILED until proven)
- **Truth Over Comfort** (Report actual state)
- **Bulletproof Verification Protocol** (4-phase verification mandatory)
- **Zero Tolerance for Theatrical Wrappers** (No mocks, no stubs, no fake data)

**Database Entry Point**: Query `agent_landing` table (version 5.0) in `aya_rag` database for complete Prime Directives context on initialization.

**Full Reference**: See `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md` for complete governance framework

---

## ⚠️ IMPORTANT: DATABASE STATUS (October 29, 2025)

**PostgreSQL 18 is the production database. YugabyteDB has been decommissioned.**

- **Production**: PostgreSQL 18 on port 5432 with database `aya_rag`
- **User**: postgres
- **Status**: All data verified intact (27,924 chunks + agent data)
- **Agent Turbo**: 128 knowledge entries with 100% embedding coverage
- **Tailscale Access**: ✅ psql -h alpha.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag
- **Remote Performance**: 78ms from AIR (excellent for remote operations)
- **Guide**: `/Users/arthurdell/AYA/POSTGRES_TAILSCALE_ACCESS.md`

## ✅ AGENT TURBO - CURSOR READY (October 29, 2025)

**Agent Turbo is fully initialized and operational for Cursor IDE with GPU acceleration!**

- **Status**: ✅ VERIFIED AND OPERATIONAL
- **GPU**: ✅ MLX enabled (80 cores - M3 Ultra)
- **Database**: PostgreSQL 18 (121 knowledge entries, 100% embedding coverage)
- **Quick Reference**: `/Users/arthurdell/AYA/AGENT_TURBO_CURSOR_QUICKREF.md`
- **Full Guide**: `/Users/arthurdell/AYA/AGENT_TURBO_CURSOR_READY.md`
- **GPU Fix Report**: `/Users/arthurdell/AYA/MLX_GPU_FIX_VERIFIED.md`

**One-line verification**:
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py verify
# Requires: required_permissions: ["all"] in Cursor
# Expected: ✅ MLX GPU acceleration enabled (80 cores)
```

## ⭐ LM STUDIO - EXCEPTIONAL CODING SKILLS VERIFIED (October 29, 2025)

**LM Studio models tested and verified with EXCEPTIONAL coding capabilities!**

- **Status**: ✅ 5 MODELS LOADED AND VERIFIED
- **API**: http://localhost:1234/v1 (OpenAI-compatible)
- **Models**: qwen3-coder-480b, qwen3-next-80b-mlx, foundation-sec-8b
- **Coding Rating**: ⭐⭐⭐⭐⭐ EXCEPTIONAL (5/5)
- **Verification Report**: `/Users/arthurdell/AYA/LM_STUDIO_CODING_VERIFICATION.md`

**Tests Passed**:
- ✅ Data Structures (LRU Cache with O(1))
- ✅ Async Programming (Producer-Consumer)
- ✅ Database Optimization (100M+ rows)
- ✅ Security Analysis (SQL injection detection)
- ✅ Distributed Systems (Rate limiter with Redis)

**Quick Test**:
```bash
curl -s http://localhost:1234/v1/models | python3 -m json.tool
# Expected: 5 models including qwen3-coder and qwen3-next-mlx
```

## 🔧 LM STUDIO MCP & CORS STATUS (October 29, 2025)

**Custom MCP implementation verified - needs bug fixes!**

- **CORS**: ✅ Enabled (wildcard `*`)
- **MCP (Native)**: ❌ Not in LM Studio
- **MCP (Custom)**: ⚠️ 85% Operational (2 bugs found)
- **Tool Calling**: ✅ Supported (MCP foundation)
- **Network**: ✅ Internal (10GbE) + External (Tailscale)
- **Full Report**: `/Users/arthurdell/AYA/LM_STUDIO_MCP_VERIFICATION_REPORT.md`

**Status**:
- ✅ LM Studio Client works perfectly
- ⚠️ MCP Server has method mismatches (fixable in ~10 min)
- ⚠️ Agent Turbo integration not initializing (import path issue)

**Critical Fixes Needed**:
1. MCP server line 63: Change `generate()` to `generate_text()`
2. MCP server line 71: Add `create_embedding()` method
3. Agent Turbo line 187: Fix import path for LM Studio client

## 🌐 TAILSCALE LM STUDIO ACCESS (October 29, 2025)

**Both ALPHA and BETA LM Studio accessible from anywhere on Tailnet!**

- **ALPHA**: ✅ https://alpha.tail5f2bae.ts.net/v1/ (5 models, 480B coder)
- **BETA**: ✅ https://beta.tail5f2bae.ts.net/v1/ (7 models)
- **Access From**: AIR, mobile, future Gamma - any Tailscale client
- **Latency**: ~17ms via Tailscale, ~15ms via 10GbE, ~10ms localhost
- **Security**: Tailnet-only (TLS encrypted, no public access)
- **Full Guide**: `/Users/arthurdell/AYA/TAILSCALE_LM_STUDIO_ACCESS_GUIDE.md`

**Quick Test**:
```bash
# From any Tailscale client
curl -k https://alpha.tail5f2bae.ts.net/v1/models
curl -k https://beta.tail5f2bae.ts.net/v1/models
```

**Python Example**:
```python
import requests
r = requests.post("https://alpha.tail5f2bae.ts.net/v1/chat/completions", 
                  verify=False, json={"model":"qwen3-coder-480b-a35b-instruct",
                  "messages":[{"role":"user","content":"Hello"}]})
print(r.json()['choices'][0]['message']['content'])
```

## 🔍 CODE VALIDATOR - CROSS-NODE AUTOMATED REVIEW (October 29, 2025)

**Automated code validation using ALPHA's LM Studio accessible from all nodes!**

- **Default Model**: qwen3-next-80b-a3b-instruct-mlx (80B, 4.6x faster than 480B)
- **Access**: Tailscale from any node (ALPHA, BETA, Gamma, AIR)
- **Performance**: 3-4s per review (ALPHA), 4-5s (cross-node via Tailscale)
- **Quality**: ⭐⭐⭐⭐⭐ Exceptional (finds SQL injection, bugs, best practices)
- **Status**: ✅ PRODUCTION READY (installed on ALPHA)
- **Guide**: `/Users/arthurdell/AYA/CODE_VALIDATOR_DEPLOYMENT_GUIDE.md`

**Quick Usage**:
```bash
# Validate any code file
./scripts/validate validate --file script.py

# Run test
./scripts/validate test

# Works from ALPHA (localhost), BETA/Gamma/AIR (Tailscale)
```

**Model Comparison** (tested with vulnerable code):
- qwen3-next-80b-mlx: 3.74s, 15 issues found ⭐ **DEFAULT**
- qwen3-coder-480b: 17.14s, 15 issues found (same quality, 4.6x slower)

---

## AYA Platform Overview

AYA is a production multi-agent orchestration platform featuring Agent Turbo (core orchestration), PostgreSQL 18 database (centralized state), distributed computing (ALPHA/BETA Mac Studio nodes), and GitHub Actions CI/CD on self-hosted runners.

**Critical Principle**: This platform enforces strict functional reality - if it doesn't run and produce queryable results, it doesn't exist. All operations use actual PostgreSQL 18, no mocks, no theatrical wrappers.

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
- No local database (uses PostgreSQL 18 on ALPHA)
- Primary use: Monitoring and control of ALPHA/BETA

### ALPHA (Mac Studio M3 Ultra - PostgreSQL Primary)

```bash
# Working directory
cd /Users/arthurdell/AYA/

# Agent Turbo operations
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_turbo.py verify

# Database operations (PostgreSQL 18 on port 5432)
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag

# Check PostgreSQL status
ps aux | grep postgres | grep -v grep
```

**ALPHA Characteristics**:
- Path: `/Users/arthurdell/AYA/` (on 16TB boot/home drive)
- Storage: 16TB internal SSD (boot/system/home - no separate DATA volume)
- PostgreSQL 18: Production database (primary instance)
- Agent Turbo workers: 10 workers running
- Blue team training and planner execution

### BETA (Mac Studio M3 Ultra - Worker Node)

```bash
# Working directory (NOTE: Different from ALPHA!)
cd /Volumes/DATA/AYA/

# Agent Turbo operations
cd /Volumes/DATA/AYA/Agent_Turbo/core
python3 agent_turbo.py verify

# Database operations (remote PostgreSQL 18 on ALPHA)
ssh alpha.tail5f2bae.ts.net "PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag"

# Check LM Studio models
curl http://localhost:1234/v1/models | python3 -m json.tool

# Docker operations
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**BETA Characteristics**:
- Path: `/Volumes/DATA/AYA/` (on separate 15TB DATA volume - not boot drive)
- No local database (uses PostgreSQL 18 on ALPHA via Tailscale)
- Agent Turbo workers: 10 workers running
- Red team generation and LLM inference
- Large dataset storage (GLADIATOR, models)
- Docker containers (red_combat, n8n-beta)

**Critical Path Differences**:
- **ALPHA**: `/Users/arthurdell/AYA/` (16TB boot/home drive - no separate DATA volume)
- **BETA**: `/Volumes/DATA/AYA/` (separate 15TB DATA volume mounted)
- **AIR**: `/Users/arthurdell/AYA/` (boot drive - no separate DATA volume)

## System Architecture

### **🚀 AGENT TURBO INITIALIZATION - START HERE**

**For any new AI agent working with AYA, initialize Agent Turbo FIRST**:

```bash
# Quick initialization (3 seconds)
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py verify
```

**Expected Output**: `✅ AGENT_TURBO: VERIFIED AND OPERATIONAL`

**If initialization fails**, see: `/Users/arthurdell/AYA/AGENT_TURBO_QUICKSTART.md`

**System Requirements**:
- PostgreSQL 18 running on port 5432
- MLX GPU acceleration (80 cores)

---

### PostgreSQL 18 Database

**Status**: PRODUCTION DATABASE (PostgreSQL 18 decommissioned October 29, 2025)

**Connection Details**:
- Host: localhost (127.0.0.1 on ALPHA)
- Port: 5432
- Database: `aya_rag`
- User: `postgres`
- Password: `Power$$336633$$`

**Quick Commands**:
```bash
# Connect to PostgreSQL 18
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag

# Check PostgreSQL status
ps aux | grep postgres | grep -v grep

# View PostgreSQL version
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT version();"
```

**Architecture**:
- Deployment: PostgreSQL 18 with Patroni HA cluster
- Primary: ALPHA (active)
- Standby: BETA (replica)
- Extensions: pgvector, uuid-ossp

---

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

### Database Schema (PostgreSQL 18 aya_rag)

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

## Tailscale Serve & LM Studio Configuration

### Tailscale Serve on ALPHA

**Service**: LM Studio API exposed via Tailscale Serve
**URL**: `https://alpha.tail5f2bae.ts.net`
**Backend**: `http://127.0.0.1:1234`
**Protocol**: HTTPS with Tailscale-issued TLS certificates
**Access**: Tailnet members only (not public internet)

**Configuration**:
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --bg --https 443 http://127.0.0.1:1234
```

**Check Status**:
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve status
```

**Disable** (if needed):
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --https=443 off
```

### Tailscale Serve on BETA

**Service**: LM Studio API exposed via Tailscale Serve
**URL**: `https://beta.tail5f2bae.ts.net`
**Backend**: `http://127.0.0.1:1234`
**Access**: Tailnet members only

### LM Studio on ALPHA

**Installation**: ✅ Installed at `/Applications/LM Studio.app`
**Server Port**: `1234`
**Network Binding**: All interfaces (`*:1234`)

#### Access Methods

1. **Localhost** (fastest for local operations):
   ```bash
   curl http://127.0.0.1:1234/v1/models
   ```

2. **Direct 10 GbE** (fastest for cross-node):
   ```bash
   # From BETA
   curl http://192.168.0.80:1234/v1/models
   ```

3. **Tailscale Serve** (portable remote access):
   ```bash
   # From any tailnet node
   curl -k https://alpha.tail5f2bae.ts.net/v1/models
   ```

#### Available Models

- `qwen3-next-80b-a3b-instruct-mlx` - Latest Qwen 80B model
- `qwen3-coder-480b-a35b-instruct` - Massive 480B coding model
- `text-embedding-nomic-embed-text-v1.5` - Embedding model
- `foundation-sec-8b-instruct-int8` - Security-focused 8B model

### LM Studio on BETA

**Installation**: ✅ Installed
**Server Port**: `1234`
**Network Binding**: All interfaces

#### Access Methods

1. **Localhost**: `http://127.0.0.1:1234/v1`
2. **Direct 10 GbE**: `http://192.168.0.20:1234/v1`
3. **Tailscale Serve**: `https://beta.tail5f2bae.ts.net`

#### Available Models

- `qwen3-next-80b-a3b-instruct-mlx`
- `qwen3-14b-mlx`
- `qwen2.5-coder-14b-instruct-mlx`
- `llama-3.3-70b-instruct`
- `tinyllama-1.1b-chat-v1.0-mlx`

### CORS & Tool Calling Status

#### CORS: ✅ ENABLED (Wildcard Origins)

LM Studio ships with CORS enabled by default:
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: *
```

**Implications**:
- ✅ Browser-based dashboards work immediately
- ✅ No proxy needed for web UIs
- ⚠️ ANY website can access your LLM (if network-accessible)
- 🔒 Mitigated by: Firewall + Tailscale network isolation

**Check CORS headers**:
```bash
curl -s -I http://localhost:1234/v1/models | grep -i "access-control"
```

#### Tool Calling: ✅ SUPPORTED

LM Studio supports OpenAI-compatible tool/function calling:

**Test**:
```bash
curl -s http://localhost:1234/v1/chat/completions -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model":"qwen3-next-80b-a3b-instruct-mlx",
    "messages":[{"role":"user","content":"test"}],
    "tools":[{
      "type":"function",
      "function":{"name":"test","description":"test tool"}
    }]
  }' | python3 -m json.tool
```

**Result**: Returns `tool_calls` array in response (foundation for MCP-like functionality)

#### MCP (Model Context Protocol): ❌ NOT NATIVELY SUPPORTED

- No dedicated MCP GUI configuration
- No `/v1/mcp` endpoint
- Tool calling provides the foundation for custom MCP implementation

**Build Custom MCP Tools**:
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Query PostgreSQL 18",
            "parameters": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file from GLADIATOR datasets",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    }
]
```

### Network Performance

#### 10 Gigabit Ethernet
- **ALPHA**: 192.168.0.80 (MTU 9000, 10Gbase-T, full-duplex)
- **BETA**: 192.168.0.20 (MTU 9000, 10Gbase-T, full-duplex)
- **Latency**: ~0.4ms average
- **Throughput**: 10 Gbps physical

#### LM Studio Latency Measurements
- **Localhost**: ~10ms
- **Direct 10 GbE**: ~15ms (ALPHA ↔ BETA)
- **Tailscale Serve**: ~17ms (2ms overhead)

**Recommendation**: Use direct 10 GbE for production Agent Turbo inference, Tailscale for remote/AIR access.

### Integration Examples

#### Agent Turbo Integration (ALPHA → ALPHA)
```python
import requests

response = requests.post(
    "http://127.0.0.1:1234/v1/chat/completions",
    json={
        "model": "qwen3-next-80b-a3b-instruct-mlx",
        "messages": [{"role": "user", "content": "Query"}]
    }
)
```

#### Agent Turbo Integration (BETA → ALPHA)
```python
# Use direct 10 GbE for best performance
response = requests.post(
    "http://192.168.0.80:1234/v1/chat/completions",
    json={
        "model": "qwen3-coder-480b-a35b-instruct",
        "messages": [{"role": "user", "content": "Generate code"}]
    }
)
```

#### n8n Workflow Integration
```json
{
  "url": "http://192.168.0.80:1234/v1/chat/completions",
  "method": "POST",
  "body": {
    "model": "qwen3-next-80b-a3b-instruct-mlx",
    "messages": [{"role": "user", "content": "{{ $json.prompt }}"}]
  }
}
```

### Documentation

**ALPHA Configuration**:
- `/Users/arthurdell/AYA/ALPHA_TAILSCALE_LM_STUDIO_STATUS.md` - Complete status
- `/Users/arthurdell/AYA/ALPHA_LM_STUDIO_CORS_MCP_FINDINGS.md` - CORS/MCP investigation

**BETA Configuration** (via SSH):
- `/Volumes/DATA/AYA/TAILSCALE_SERVE_TAILDROP_SETUP_2025-10-28.md`
- `/Volumes/DATA/AYA/LM_STUDIO_DUAL_ACCESS_CONFIGURATION.md`
- `/Volumes/DATA/AYA/LM_STUDIO_CORS_MCP_EXPERT_GUIDE.md` (40KB expert guide)

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

**Note**: PostgreSQL 18 is now the primary database. PostgreSQL 18 is deprecated.

```bash
# Connect to PostgreSQL 18 (always use localhost/127.0.0.1)
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18 \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag

# Check database size and table count
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18 \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag -c "
SELECT pg_size_pretty(pg_database_size('aya_rag')) as size,
       (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public') as tables;"

# Check active agent sessions
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18 \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag -c "
SELECT session_id, agent_platform, agent_role, status, created_at
FROM agent_sessions
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10;"

# Check recent tasks
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18 \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag -c "
SELECT task_id, task_type, status, task_description
FROM agent_tasks
ORDER BY created_at DESC
LIMIT 10;"

# View audit trail
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18 \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag -c "
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
