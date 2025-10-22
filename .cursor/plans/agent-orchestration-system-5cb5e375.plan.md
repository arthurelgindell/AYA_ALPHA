<!-- 5cb5e375-15a1-4cf7-89c8-2f34d66dc850 b2b6a3e3-97c4-4558-a0f1-409de97fa094 -->
# Agent Turbo PostgreSQL Migration & Multi-Agent Orchestration

## PRIME DIRECTIVES COMPLIANCE MANDATORY

**Core Principle**: "If it doesn't run, it doesn't exist" - Every component MUST be verified functional with terminal output proof.

## Phase 1: PostgreSQL Schema Design & Verification (45 minutes)

### 1.1 Create Schema Migration Script

File: `/Users/arthurdell/AYA/services/migrate_agent_turbo_schema.sql`

Contains 6 tables with indexes. Each table MUST be verified after creation.

**Tables:**

- agent_sessions - Track all agent sessions
- agent_tasks - Stateful task assignments  
- agent_knowledge - Migrated from SQLite with pgvector
- agent_actions - Complete audit trail
- agent_context_cache - Landing context snapshots
- Plus all indexes for performance

### 1.2 Execute Schema Migration

```bash
cd /Users/arthurdell/AYA/services
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -f migrate_agent_turbo_schema.sql
```

### 1.3 MANDATORY VERIFICATION (Directive #1: FUNCTIONAL REALITY)

```bash
# Verify all tables exist
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "\dt agent_*"
# MUST show 6 tables

# Verify agent_sessions schema
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "\d agent_sessions"
# MUST show all columns

# Test INSERT/SELECT (Directive #11: NO THEATRICAL WRAPPERS)
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
INSERT INTO agent_sessions (session_id, agent_platform, agent_role, landing_context, status) 
VALUES ('test_001', 'claude_code', 'planner', '{}'::jsonb, 'active') 
RETURNING *;"
# MUST return actual row data

# Verify data persisted
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT * FROM agent_sessions WHERE session_id = 'test_001';"
# MUST show the inserted row

# Cleanup test data
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "DELETE FROM agent_sessions WHERE session_id = 'test_001';"
```

**FAILURE PROTOCOL (Directive #6):** If ANY verification fails, state "TASK FAILED", show error, STOP immediately.

## Phase 2: PostgreSQL Connector (30 minutes)

### 2.1 Create postgres_connector.py

File: `/Users/arthurdell/AYA/Agent_Turbo/core/postgres_connector.py`

- ThreadedConnectionPool (2-10 connections)
- Auto connection management
- RealDictCursor for easy access
- Error handling

### 2.2 MANDATORY VERIFICATION (Directive #10: SYSTEM VERIFICATION)

```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core

# Test import
python3 -c "from postgres_connector import PostgreSQLConnector; print('✅ Import successful')"
# MUST print success message

# Test connection
python3 -c "
from postgres_connector import PostgreSQLConnector
db = PostgreSQLConnector()
result = db.execute_query('SELECT 1 as test', fetch=True)
print(f'✅ Query result: {result}')
print(f'✅ Pool config: {db.pool.minconn}-{db.pool.maxconn} connections')
"
# MUST show: [{'test': 1}] and Pool: 2-10

# Test actual database query
python3 -c "
from postgres_connector import PostgreSQLConnector
db = PostgreSQLConnector()
result = db.execute_query('SELECT COUNT(*) as count FROM system_nodes', fetch=True)
print(f'✅ System nodes: {result[0][\"count\"]}')
"
# MUST show actual count (should be 2)
```

**NO MOCKS ALLOWED (Directive #11)**: Every test MUST query actual PostgreSQL database.

## Phase 3: Agent Turbo PostgreSQL Refactor (2-3 hours)

### 3.1 Refactor agent_turbo.py

File: `/Users/arthurdell/AYA/Agent_Turbo/core/agent_turbo.py`

Key changes:

- Replace SQLite with PostgreSQLConnector
- Update add() to use agent_knowledge table
- Update query() to use pgvector similarity
- Generate embeddings via existing service (port 8765)
- Maintain RAM disk caching

### 3.2 BULLETPROOF VERIFICATION (Directive #5)

**Component Verification:**

```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core

# Test embedding service connectivity
curl -s http://localhost:8765/health
# MUST return {"status":"healthy","metal_available":true,"model_loaded":true}

# Test add() method
python3 -c "
from agent_turbo import AgentTurbo
at = AgentTurbo()
result = at.add('Test knowledge entry for verification')
print(result)
"
# MUST show: ✅ Added knowledge: <hash>

# Verify in database
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT COUNT(*) FROM agent_knowledge;"
# MUST show count > 0

# Test query() method
python3 -c "
from agent_turbo import AgentTurbo
at = AgentTurbo()
result = at.query('verification', limit=3)
print(result)
"
# MUST show actual results with similarity scores
```

**Integration Verification:**

```bash
# Add 3 entries
python3 -c "
from agent_turbo import AgentTurbo
at = AgentTurbo()
at.add('PostgreSQL is a powerful database')
at.add('Python is a programming language')
at.add('MLX provides GPU acceleration')
"

# Query and verify results
python3 -c "
from agent_turbo import AgentTurbo
at = AgentTurbo()
result = at.query('database', limit=2)
print(result)
"
# MUST show 'PostgreSQL' result with highest similarity
```

**Performance Verification:**

```bash
# Benchmark query time
python3 -c "
import time
from agent_turbo import AgentTurbo
at = AgentTurbo()
start = time.time()
result = at.query('test query', limit=5)
elapsed_ms = (time.time() - start) * 1000
print(f'Query time: {elapsed_ms:.2f}ms')
print(f'Result: {len(result.split(chr(10)))} lines')
"
# MUST complete in <500ms for uncached, <100ms for cached
```

## Phase 4: Agent Orchestration Module (3-4 hours)

### 4.1 Create agent_orchestrator.py

File: `/Users/arthurdell/AYA/Agent_Turbo/core/agent_orchestrator.py`

Core methods:

- initialize_agent_session() - with landing context
- generate_landing_context() - complete system state
- create_task() - task delegation
- log_agent_action() - audit trail
- get_session_history() - complete history

### 4.2 MANDATORY FUNCTIONAL VERIFICATION (Directive #1)

```python
# Test agent session initialization
python3 -c "
from agent_orchestrator import AgentOrchestrator
orch = AgentOrchestrator()
session = orch.initialize_agent_session('claude_code', 'planner')
print(f'✅ Session ID: {session[\"session_id\"]}')
print(f'✅ Context keys: {list(session[\"landing_context\"].keys())}')
print(f'✅ System nodes: {len(session[\"landing_context\"][\"system_nodes\"])}')
"
# MUST show actual session_id, real context keys, actual node count

# Verify session in database
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT session_id, agent_platform, agent_role, status 
FROM agent_sessions 
WHERE agent_platform = 'claude_code' 
ORDER BY created_at DESC LIMIT 1;"
# MUST show the session just created

# Test landing context generation
python3 -c "
from agent_orchestrator import AgentOrchestrator
orch = AgentOrchestrator()
context = orch.generate_landing_context()
print(f'System nodes: {len(context[\"system_nodes\"])}')
print(f'Active services: {len(context[\"active_services\"])}')
print(f'Doc sources: {len(context[\"documentation_sources\"])}')
print(f'Database size: {context[\"database_stats\"][\"total_size_mb\"]} MB')
"
# MUST show actual counts from database

# Test task creation
python3 -c "
from agent_orchestrator import AgentOrchestrator
orch = AgentOrchestrator()
session = orch.initialize_agent_session('test', 'planner')
task_id = orch.create_task(
    session['session_id'], 
    'test_task', 
    'Test task description',
    'executor',
    priority=7
)
print(f'✅ Task created: {task_id}')
"
# MUST return task_id

# Verify task in database
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT task_id, task_type, task_description, status, task_priority 
FROM agent_tasks 
ORDER BY created_at DESC LIMIT 1;"
# MUST show the task just created
```

### 4.3 Context Caching Performance Test

```python
# Test context caching
python3 -c "
import time
from agent_orchestrator import AgentOrchestrator
orch = AgentOrchestrator()

# First generation (fresh)
start = time.time()
context1 = orch.generate_landing_context()
fresh_ms = (time.time() - start) * 1000
print(f'Fresh context: {fresh_ms:.2f}ms')

# Second generation (should be faster if cached)
start = time.time()
context2 = orch.get_cached_landing_context()
cached_ms = (time.time() - start) * 1000
print(f'Cached context: {cached_ms:.2f}ms')
print(f'Cache speedup: {fresh_ms / cached_ms:.1f}x')
"
# Cached MUST be <100ms, ideally <50ms
```

## Phase 5: Claude Code Planner Interface (1-2 hours)

### 5.1 Create claude_planner.py

File: `/Users/arthurdell/AYA/Agent_Turbo/core/claude_planner.py`

Methods:

- start_planning_session() - Initialize with landing context
- format_landing_context() - Human-readable prompt
- create_delegated_task() - Task delegation
- audit_task_results() - Audit completed work

### 5.2 END-TO-END WORKFLOW VERIFICATION (Directive #10)

```python
# Complete workflow test
python3 -c "
from claude_planner import ClaudePlanner

# Initialize planner
planner = ClaudePlanner()
session = planner.start_planning_session()
print(f'✅ Planner session: {session[\"session_id\"]}')
print(f'✅ Context prompt length: {len(session[\"landing_context_prompt\"])} chars')

# Delegate task
task_id = planner.create_delegated_task(
    'Implement feature X',
    'implementation',
    'executor',
    priority=8
)
print(f'✅ Task delegated: {task_id}')

# Verify audit trail
from agent_orchestrator import AgentOrchestrator
orch = AgentOrchestrator()
history = orch.get_session_history(session['session_id'])
print(f'✅ Session tasks: {len(history[\"tasks\"])}')
print(f'✅ Session actions: {len(history[\"actions\"])}')
"
# MUST show actual session, task, and audit trail data

# Verify in database
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT 
    s.session_id,
    s.agent_role,
    COUNT(DISTINCT t.task_id) as task_count,
    COUNT(DISTINCT a.action_id) as action_count
FROM agent_sessions s
LEFT JOIN agent_tasks t ON s.session_id = t.session_id
LEFT JOIN agent_actions a ON s.session_id = a.session_id
WHERE s.agent_role = 'planner'
GROUP BY s.session_id, s.agent_role
ORDER BY s.created_at DESC LIMIT 1;"
# MUST show the planner session with task and action counts
```

## Phase 6: Migration Script & Testing (2-3 hours)

### 6.1 Create migrate_agent_turbo.py

File: `/Users/arthurdell/AYA/services/migrate_agent_turbo.py`

Migrate existing SQLite data to PostgreSQL:

1. Connect to both databases
2. Export SQLite knowledge entries
3. Generate embeddings
4. Import to PostgreSQL
5. Verify counts match

### 6.2 Performance Benchmark

```bash
# Create benchmark script
python3 -c "
import time
from agent_turbo import AgentTurbo

at = AgentTurbo()

# Add 100 entries
start = time.time()
for i in range(100):
    at.add(f'Test entry number {i} with unique content')
add_time = time.time() - start
print(f'Add 100 entries: {add_time:.2f}s ({add_time*10:.1f}ms per entry)')

# Query 100 times
start = time.time()
for i in range(100):
    at.query(f'test query {i % 10}', limit=5)
query_time = time.time() - start
print(f'100 queries: {query_time:.2f}s ({query_time*10:.1f}ms per query)')
"
# Targets: <50ms per add, <100ms per query
```

### 6.3 Load Testing

```python
# Concurrent session test
python3 -c "
import concurrent.futures
from agent_orchestrator import AgentOrchestrator

def create_session(i):
    orch = AgentOrchestrator()
    platform = ['claude_code', 'openai', 'gemini'][i % 3]
    role = ['planner', 'executor', 'validator'][i % 3]
    session = orch.initialize_agent_session(platform, role)
    return session['session_id']

# Create 50 concurrent sessions
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(create_session, range(50)))

print(f'✅ Created {len(results)} concurrent sessions')
print(f'✅ Sample IDs: {results[:3]}')
"
# MUST complete without errors, all sessions persisted
```

## VERIFICATION CHECKLIST (Before Claiming Success)

### Phase 1 Complete:

- [ ] All 6 tables created in aya_rag
- [ ] All indexes created
- [ ] INSERT test successful
- [ ] SELECT test retrieves data
- [ ] Terminal output proof provided

### Phase 2 Complete:

- [ ] PostgreSQLConnector imports successfully
- [ ] Connection pool created (2-10)
- [ ] Query execution works
- [ ] Actual database data retrieved
- [ ] Terminal output proof provided

### Phase 3 Complete:

- [ ] agent_turbo.py refactored
- [ ] Embedding service connectivity verified
- [ ] add() method writes to PostgreSQL
- [ ] query() method uses pgvector
- [ ] Performance <500ms per query
- [ ] Terminal output proof provided

### Phase 4 Complete:

- [ ] agent_orchestrator.py functional
- [ ] Session initialization works
- [ ] Landing context has real data
- [ ] Tasks can be created
- [ ] Audit trail logs actions
- [ ] Terminal output proof provided

### Phase 5 Complete:

- [ ] claude_planner.py functional
- [ ] Planning session starts
- [ ] Tasks can be delegated
- [ ] Audit trail verifiable
- [ ] End-to-end workflow tested
- [ ] Terminal output proof provided

### Phase 6 Complete:

- [ ] SQLite data migrated
- [ ] Performance benchmarks passed
- [ ] Load testing successful
- [ ] 100+ concurrent sessions work
- [ ] Terminal output proof provided

## FAILURE PROTOCOL

If ANY verification fails:

1. Output: "TASK FAILED: [specific failure]"
2. Show actual error message
3. Do NOT minimize or continue
4. Trace to root cause
5. Fix and re-verify before proceeding

## SUCCESS CRITERIA

System is COMPLETE when:

1. All 6 phases verified with terminal output
2. Agent Turbo queries PostgreSQL (not SQLite)
3. Landing context generates in <100ms (cached)
4. Multi-agent sessions work
5. Complete audit trail exists
6. 100+ concurrent sessions tested
7. Zero theatrical wrappers present
8. All code actually runs and produces results

**NO claims without proof. NO mocks. NO shortcuts.**

### To-dos

- [ ] Create and execute PostgreSQL schema migration, verify 6 tables with terminal proof
- [ ] Build PostgreSQL connector with connection pooling, verify with actual queries
- [ ] Refactor agent_turbo.py for PostgreSQL, verify add/query with real data
- [ ] Build AgentOrchestrator, verify session init and landing context with actual DB queries
- [ ] Create ClaudePlanner interface, verify end-to-end workflow with terminal proof
- [ ] Migrate SQLite data, run performance and load tests with measurements