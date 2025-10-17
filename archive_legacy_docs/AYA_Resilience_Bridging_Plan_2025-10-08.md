# AYA UNIFIED KNOWLEDGE BASE - RESILIENCE BRIDGING PLAN

**Document Type:** Execution Bridge Plan  
**Date:** 2025-10-08 12:15 UTC+4  
**Author:** cursor  
**System:** ALPHA.local → Full Cluster  

**Reference Documents:**
- Source: `aya_master_2025-10-06_00-10-02.md` (Architecture Specification)
- Current State: `ALPHA_PostgreSQL_Production_Audit_2025-10-08.md` (Live Audit)

---

## EXECUTIVE SUMMARY

This document bridges the gap between **current operational state** and **target resilient architecture**. ALPHA primary database is operational (Phase 1 complete), but critical resilience components are offline or incomplete.

**Gap Analysis:**
- ✅ Phase 1: ALPHA Primary Database - **COMPLETE**
- ⚠️ Phase 2: BETA Replica - **PARTIALLY COMPLETE** (slot configured, replica offline)
- ❌ Phase 3: AIR Client - **STATUS UNKNOWN** (not verified)
- ❌ Phase 4: MCP Servers - **STATUS UNKNOWN** (not verified)
- ❌ Embedding Service - **DOWN** (critical for ingestion)

**Objective:** Achieve full resilience with zero data loss capability, sub-60-second failover, and operational embedding service.

---

## ARCHITECTURE ALIGNMENT MATRIX

### Current State vs. Target Architecture

| Component | Target (aya_master) | Current (audit) | Gap | Priority |
|-----------|-------------------|-----------------|-----|----------|
| **ALPHA Primary DB** | PostgreSQL 18, aya_rag, operational | ✅ PostgreSQL 18.0, aya_rag, 23h uptime | None | ✅ |
| **ALPHA Embedding Service** | Running on port 8765, MLX-accelerated | ❌ Not running (stale PID) | Service down | 🔴 P1 |
| **BETA PostgreSQL** | PostgreSQL 18 installed | ⚠️ Unknown (not audited) | Needs verification | 🟡 P2 |
| **BETA Replication** | Streaming from ALPHA, <100ms lag | ❌ Slot exists but inactive | Replica not connected | 🔴 P1 |
| **BETA Embedding Service** | Running on port 8765 | ⚠️ Unknown (not audited) | Needs verification | 🟡 P2 |
| **AIR PostgreSQL** | Local database with sync daemon | ⚠️ Unknown (not in audit scope) | Needs verification | 🟢 P3 |
| **AIR Sync Daemon** | Pull-based, 60s intervals | ⚠️ Unknown (not in audit scope) | Needs verification | 🟢 P3 |
| **MCP Servers** | Deployed on all 3 systems | ⚠️ Unknown (not verified) | Needs verification | 🟢 P3 |
| **Replication Lag** | <100ms (ALPHA→BETA) | N/A (no active replication) | Zero replication active | 🔴 P1 |
| **Failover Capability** | Sub-60-second promotion | ❌ Not possible (BETA offline) | No hot standby | 🔴 P1 |

**Critical Path:** P1 items must be resolved to achieve resilience. P2 items required for full redundancy. P3 items for complete architecture.

---

## GAP ANALYSIS DETAILS

### Gap 1: Embedding Service Offline (ALPHA)
**Status:** CRITICAL  
**Impact:** New document ingestion completely blocked  
**Current State:** Process not running, stale PID file exists  
**Target State:** FastAPI service on port 8765, MLX Metal-accelerated, responding to health checks  
**Estimated Time:** 15 minutes  
**Risk Level:** LOW (restart operation, no data risk)

### Gap 2: BETA Replica Not Connected
**Status:** CRITICAL  
**Impact:** No failover capability, single point of failure  
**Current State:** Replication slot `beta_slot` configured but inactive, 0 active replication streams  
**Target State:** BETA streaming from ALPHA with <100ms lag, read-only replica operational  
**Estimated Time:** 45-60 minutes  
**Risk Level:** MEDIUM (requires BETA system access, base backup if not already done)

### Gap 3: BETA System Status Unknown
**Status:** HIGH  
**Impact:** Cannot verify replica capability  
**Current State:** Not audited in current assessment  
**Target State:** BETA accessible, PostgreSQL installed and configured  
**Estimated Time:** 5 minutes (verification only)  
**Risk Level:** LOW (read-only audit)

### Gap 4: AIR Client Status Unknown
**Status:** MEDIUM  
**Impact:** Mobile client offline operation not available  
**Current State:** Not verified in current audit  
**Target State:** AIR with local PostgreSQL, sync daemon, write queue functional  
**Estimated Time:** 30-60 minutes (if incomplete)  
**Risk Level:** MEDIUM (requires AIR system access)

### Gap 5: MCP Server Deployment Unknown
**Status:** MEDIUM  
**Impact:** IDE integration not available  
**Current State:** Not verified in current audit  
**Target State:** MCP servers deployed and functional on all systems  
**Estimated Time:** 30-45 minutes (if incomplete)  
**Risk Level:** LOW (application layer only)

---

## EXECUTION PLAN - PHASED APPROACH

### PHASE A: CRITICAL RESILIENCE RESTORATION (Priority 1)
**Objective:** Restore embedding service and establish BETA replication  
**Duration:** 60-75 minutes  
**Prerequisites:** ALPHA operational (✅ confirmed), BETA system accessible

#### A1: Verify BETA System Accessibility
**Duration:** 5 minutes  
**Type:** Read-only verification  
**Risk:** None

**Steps:**
```bash
# From ALPHA, verify BETA reachable
ping -c 3 192.168.0.20

# Verify Tailscale connectivity
ping -c 3 100.89.227.75

# Test SSH access
ssh arthurdell@192.168.0.20 "hostname && uname -a"

# Expected: BETA.local, Darwin kernel info
```

**Success Criteria:**
- ✅ BETA responds to ping (both interfaces)
- ✅ SSH connection succeeds
- ✅ Hostname confirms BETA.local

**Failure Protocol:**
- If BETA unreachable: STOP. Document network issue, escalate to network troubleshooting
- If SSH fails: STOP. Document authentication issue, verify SSH keys

---

#### A2: Audit BETA PostgreSQL Status
**Duration:** 10 minutes  
**Type:** Read-only verification  
**Risk:** None

**Steps:**
```bash
# SSH to BETA
ssh arthurdell@192.168.0.20

# Check PostgreSQL installed
psql --version
# Expected: PostgreSQL 18.0 (or match ALPHA version)

# Check if PostgreSQL running
ps aux | grep postgres | grep -v grep

# Check port status
netstat -an | grep LISTEN | grep 5432

# If running, check recovery mode
psql -U postgres -d aya_rag -c "SELECT pg_is_in_recovery();"
# Expected: t (true, in recovery mode)

# Check standby.signal file
ls -la /Volumes/DATA/AYA/data/standby.signal
# Expected: File exists if replica configured

# Check primary connection config
grep primary_conninfo /Volumes/DATA/AYA/data/postgresql.auto.conf
```

**Success Criteria:**
- ✅ PostgreSQL 18.0 installed
- ✅ PostgreSQL process running OR ready to start
- ✅ Port 5432 available (listening or available)

**Document Findings:**
- PostgreSQL status: [RUNNING | STOPPED | NOT INSTALLED]
- Recovery mode: [TRUE | FALSE | N/A]
- standby.signal: [EXISTS | MISSING]
- Data directory: [EXISTS | MISSING]

**Decision Tree:**
- **If PostgreSQL running in recovery mode with standby.signal:** Proceed to A4 (connection troubleshooting)
- **If PostgreSQL stopped but data directory exists:** Proceed to A3 (restart)
- **If PostgreSQL not installed or no data directory:** ESCALATE (requires Phase 2 from master plan)

---

#### A3: Restart ALPHA Embedding Service
**Duration:** 15 minutes  
**Type:** Service restart  
**Risk:** LOW (application layer, no database impact)

**Steps:**
```bash
# On ALPHA
cd /Users/arthurdell/AYA/services

# Check if old process somehow still running (cleanup)
ps aux | grep embedding_service | grep -v grep
# If found, kill: kill -9 <PID>

# Remove stale PID file
rm -f embedding_service.pid

# Check if embedding_service.py exists
ls -la embedding_service.py
# Expected: File exists

# Check Python dependencies
python3 -c "import mlx, sentence_transformers, fastapi, uvicorn; print('Dependencies OK')"
# Expected: "Dependencies OK" (no import errors)

# Start embedding service
nohup uvicorn embedding_service:app --host 0.0.0.0 --port 8765 > embedding.log 2>&1 &

# Capture PID
echo $! > embedding_service.pid

# Wait for startup
sleep 15

# Verify process running
ps -p $(cat embedding_service.pid) > /dev/null 2>&1 && echo "RUNNING" || echo "FAILED"

# Test health endpoint
curl -s http://localhost:8765/health | python3 -m json.tool

# Expected output:
# {
#   "status": "healthy",
#   "metal_available": true
# }

# Test embedding generation
curl -X POST http://localhost:8765/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Test embedding verification"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Vector length: {len(data[\"embedding\"])}, Cached: {data[\"cached\"]}')"

# Expected: Vector length: 768, Cached: False
```

**Success Criteria:**
- ✅ Process running with valid PID
- ✅ Health check returns "healthy"
- ✅ Metal acceleration available (true)
- ✅ Embedding generation functional (768-dimensional vector)

**Verification:**
```bash
# Final verification
curl -s http://localhost:8765/stats | python3 -m json.tool
# Should show cache_size and metal_active_memory
```

**Failure Protocol:**
- If import errors: Document missing dependencies, install required packages
- If port 8765 in use: Document conflict, identify conflicting process
- If Metal not available: Document issue but continue (will use CPU fallback)
- If embedding generation fails: STOP. Document error, check model download

**Rollback:** Kill process, restore previous state (already non-functional, no rollback needed)

---

#### A4: Establish BETA Replication Connection
**Duration:** 30-45 minutes  
**Type:** Replication configuration and activation  
**Risk:** MEDIUM (requires BETA restart if config changes needed)

**Preconditions:**
- BETA PostgreSQL installed and accessible (verified in A2)
- ALPHA replication slot exists (✅ confirmed: beta_slot)
- Network connectivity confirmed (verified in A1)

**Decision Point - Data Directory Status:**

**Scenario 1: BETA has existing data directory with standby.signal**
```bash
# On BETA
ssh arthurdell@192.168.0.20

# Verify standby configuration
cat /Volumes/DATA/AYA/data/postgresql.auto.conf | grep primary_conninfo
# Should show connection to ALPHA (100.106.113.76)

# Check if PostgreSQL running
ps aux | grep postgres | grep -v grep

# If not running, start it
# Option A: If using launchd (check for plist)
sudo launchctl load /Library/LaunchDaemons/postgresql-18.plist

# Option B: If manual startup
su - postgres -c "/Library/PostgreSQL/18/bin/pg_ctl start -D /Volumes/DATA/AYA/data"

# Wait for startup
sleep 10

# Verify recovery mode
psql -U postgres -d aya_rag -c "SELECT pg_is_in_recovery();"
# Expected: t (true)

# Check replication status
psql -U postgres -d aya_rag -c "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;"
# Expected: <1 second or NULL if fully synchronized
```

**Scenario 2: BETA PostgreSQL installed but no data directory**
```bash
# CRITICAL: This requires base backup from ALPHA
# Estimated additional time: 30 minutes

# On BETA - Stop PostgreSQL if running
sudo launchctl unload /Library/LaunchDaemons/postgresql-18.plist 2>/dev/null || true

# Remove any existing data directory
rm -rf /Volumes/DATA/AYA/data

# Create .pgpass for passwordless connection
echo "100.106.113.76:5432:*:postgres:ALPHA_POSTGRES_PASSWORD" > ~/.pgpass
chmod 600 ~/.pgpass

# Create base backup from ALPHA
pg_basebackup \
  -h 100.106.113.76 \
  -U postgres \
  -D /Volumes/DATA/AYA/data \
  -P \
  -R \
  --slot=beta_slot \
  --checkpoint=fast

# This will show progress, wait for completion
# Expected output: [timestamp]/[size] kB (100%), 1/1 tablespace

# Verify standby.signal created
ls /Volumes/DATA/AYA/data/standby.signal
# Expected: File exists

# Set proper permissions
chown -R postgres:postgres /Volumes/DATA/AYA/data
chmod 700 /Volumes/DATA/AYA/data

# Start PostgreSQL
sudo launchctl load /Library/LaunchDaemons/postgresql-18.plist

# Wait for startup
sleep 15
```

**Verification Steps (Both Scenarios):**
```bash
# On BETA - Verify recovery mode
psql -U postgres -d aya_rag -c "SELECT pg_is_in_recovery();"
# Expected: t (true)

# Check replication lag
psql -U postgres -d aya_rag -c "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;"
# Expected: <1 second (essentially zero)

# Test read-only nature
psql -U postgres -d aya_rag -c "INSERT INTO documents (content) VALUES ('test');" 2>&1 | grep "read-only"
# Expected: Error message containing "read-only"

# Count synchronized data
psql -U postgres -d aya_rag -c "SELECT COUNT(*) FROM documents; SELECT COUNT(*) FROM chunks;"
# Expected: 1 document, 1 chunk (matching ALPHA)

# On ALPHA - Verify replication connection active
ssh arthurdell@192.168.0.80
psql -U postgres -c "SELECT application_name, client_addr, state, sync_state FROM pg_stat_replication;"
# Expected: walreceiver | 100.89.227.75 | streaming | async

# Verify replication slot active
psql -U postgres -c "SELECT slot_name, active, active_pid FROM pg_replication_slots WHERE slot_name = 'beta_slot';"
# Expected: beta_slot | t | <PID>

# Test real-time replication
# On ALPHA - Insert test record
psql -U postgres -d aya_rag -c "INSERT INTO documents (content, category) VALUES ('Replication test $(date +%s)', 'test') RETURNING id;"
# Note the returned ID

# On BETA - Verify record appears (within 2 seconds)
sleep 2
psql -U postgres -d aya_rag -c "SELECT content FROM documents WHERE category = 'test' ORDER BY id DESC LIMIT 1;"
# Expected: Test record visible

# Cleanup test data (on ALPHA only)
psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE category = 'test';"
```

**Success Criteria:**
- ✅ BETA in recovery mode (pg_is_in_recovery = true)
- ✅ Replication lag <1 second
- ✅ BETA is read-only (INSERT fails as expected)
- ✅ ALPHA shows active replication stream to BETA
- ✅ beta_slot active on ALPHA
- ✅ Real-time data replication verified (INSERT on ALPHA appears on BETA)

**Failure Protocol:**
- If connection refused: Check pg_hba.conf on ALPHA, verify BETA IP allowed
- If authentication fails: Verify .pgpass, check PostgreSQL user password
- If replication lag >5 seconds: Check network latency, investigate BETA performance
- If slot not active: Check BETA logs for connection errors

**Rollback:** 
- Stop BETA PostgreSQL: `sudo launchctl unload /Library/LaunchDaemons/postgresql-18.plist`
- Document state for investigation

---

#### A5: Phase A Verification Checkpoint
**Duration:** 10 minutes  
**Type:** Comprehensive verification  
**Risk:** None (read-only)

**Verification Matrix:**

| Component | Test | Expected | Command |
|-----------|------|----------|---------|
| ALPHA Embedding | Health check | "healthy" + metal_available: true | `curl http://localhost:8765/health` |
| ALPHA Embedding | Vector generation | 768-dimensional vector | `curl -X POST ...` |
| ALPHA Replication | Active streams | 1 stream to BETA | `SELECT * FROM pg_stat_replication;` |
| ALPHA Replication | Slot active | beta_slot active = true | `SELECT * FROM pg_replication_slots;` |
| BETA Recovery | Recovery mode | true | `SELECT pg_is_in_recovery();` |
| BETA Replication | Lag | <1 second | `SELECT pg_last_xact_replay_timestamp();` |
| BETA Read-only | Write fails | Error: read-only | `INSERT test` |
| End-to-End | Data sync | Record appears on BETA | Insert on ALPHA, query on BETA |

**Success Criteria:** ALL 8 tests PASS

**Deliverable:** Document all test results in Phase A Completion Report

---

### PHASE B: SYSTEM VERIFICATION AND AIR CLIENT (Priority 2-3)
**Objective:** Verify AIR client status and complete deployment if needed  
**Duration:** 30-60 minutes  
**Prerequisites:** Phase A complete

#### B1: Audit AIR System Status
**Duration:** 10 minutes  
**Type:** Read-only verification  
**Risk:** None

**Steps:**
```bash
# Check AIR accessibility
ping -c 3 100.103.127.52

# SSH to AIR
ssh arthurdell@100.103.127.52 "hostname && uname -a"
# Expected: AIR.local (or AIR hostname), Darwin kernel

# Check PostgreSQL installed
ssh arthurdell@100.103.127.52 "psql --version"

# Check if PostgreSQL running
ssh arthurdell@100.103.127.52 "ps aux | grep postgres | grep -v grep"

# Check local database exists
ssh arthurdell@100.103.127.52 "psql -U postgres -l | grep aya_rag"

# Check sync daemon
ssh arthurdell@100.103.127.52 "ps aux | grep air_sync_daemon | grep -v grep"

# Check write_queue table exists
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c '\dt' | grep write_queue"
```

**Document Findings:**
- AIR PostgreSQL: [OPERATIONAL | NOT INSTALLED | STOPPED]
- aya_rag database: [EXISTS | MISSING]
- Sync daemon: [RUNNING | STOPPED | NOT INSTALLED]
- Write queue: [EXISTS | MISSING]

**Decision Tree:**
- If all components operational: Skip to B3 (verification)
- If partial deployment: Document gaps, proceed to B2
- If not deployed: Requires Phase 3 from master plan (30-60 minutes)

---

#### B2: Deploy/Fix AIR Client (If Needed)
**Duration:** 30-45 minutes  
**Type:** Deployment or repair  
**Risk:** MEDIUM (requires AIR system access)

**Note:** This step only executes if B1 identifies missing components. Refer to Phase 3 of `aya_master_2025-10-06_00-10-02.md` for detailed deployment steps (Steps 3.1 through 3.14).

**Key Components to Deploy:**
1. PostgreSQL 18 with pgvector
2. Local aya_rag database with schema
3. write_queue table for offline operations
4. Sync daemon (air_sync_daemon.py)
5. Embedding service (local instance)

**Success Criteria:** All components from B1 audit operational

---

#### B3: Verify AIR Sync Functionality
**Duration:** 15 minutes  
**Type:** End-to-end functional test  
**Risk:** LOW (test operations only)

**Steps:**
```bash
# On ALPHA - Insert test document
psql -U postgres -d aya_rag -c "INSERT INTO documents (content, category, source) VALUES ('AIR sync test $(date +%s)', 'test', 'air_sync_test') RETURNING id;"
# Note the ID

# Wait for AIR sync cycle (60 seconds)
sleep 65

# On AIR - Verify document synchronized
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c \"SELECT content FROM documents WHERE source = 'air_sync_test';\""
# Expected: Test document visible

# On AIR - Test offline write queue
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c \"INSERT INTO write_queue (operation, table_name, data) VALUES ('INSERT', 'documents', '{\\\"content\\\": \\\"AIR offline test\\\", \\\"category\\\": \\\"test\\\", \\\"source\\\": \\\"air_offline_test\\\"}'::jsonb);\""

# Wait for sync cycle
sleep 65

# On AIR - Check if queued write synced
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c \"SELECT synced FROM write_queue WHERE data->>'source' = 'air_offline_test';\""
# Expected: synced = t

# On ALPHA - Verify write propagated
psql -U postgres -d aya_rag -c "SELECT content FROM documents WHERE source = 'air_offline_test';"
# Expected: Test document visible

# Cleanup test data
psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE source IN ('air_sync_test', 'air_offline_test');"
```

**Success Criteria:**
- ✅ ALPHA writes propagate to AIR within 65 seconds
- ✅ AIR write queue functions (queued write syncs to ALPHA)
- ✅ Cleanup successful (no orphaned test data)

---

### PHASE C: MCP SERVER DEPLOYMENT (Priority 3)
**Objective:** Deploy and verify MCP servers on all systems  
**Duration:** 30-45 minutes  
**Prerequisites:** Phases A and B complete

#### C1: Audit MCP Server Status
**Duration:** 10 minutes  
**Type:** Read-only verification  
**Risk:** None

**Steps:**
```bash
# On ALPHA
ls -la /Users/arthurdell/Agent/mcp_servers/aya_postgres_mcp_server.py
# Expected: File exists

# Test MCP server responds
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python3 /Users/arthurdell/Agent/mcp_servers/aya_postgres_mcp_server.py 2>/dev/null
# Expected: JSON response with capabilities

# On BETA
ssh arthurdell@192.168.0.20 "ls -la /Users/arthurdell/Agent/mcp_servers/aya_postgres_mcp_server.py"

# On AIR
ssh arthurdell@100.103.127.52 "ls -la /Users/arthurdell/Agent/mcp_servers/aya_postgres_mcp_server.py"
```

**Document Findings:**
- ALPHA MCP: [DEPLOYED | MISSING]
- BETA MCP: [DEPLOYED | MISSING]
- AIR MCP: [DEPLOYED | MISSING]

---

#### C2: Deploy MCP Servers (If Needed)
**Duration:** 20-30 minutes  
**Type:** Deployment  
**Risk:** LOW (application layer only)

**Note:** Refer to Phase 4 of `aya_master_2025-10-06_00-10-02.md` for detailed deployment steps (Steps 4.1 through 4.5).

**Key Components:**
1. aya_postgres_mcp_server.py implementation
2. Executable permissions set
3. Deployed to all three systems
4. Environment variables configured

---

#### C3: MCP Integration Test
**Duration:** 10 minutes  
**Type:** Functional test  
**Risk:** LOW

**Steps:**
```bash
# Test query operation
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query_aya_rag","arguments":{"query":"prime directives","limit":1}}}' | python3 /Users/arthurdell/Agent/mcp_servers/aya_postgres_mcp_server.py 2>/dev/null | python3 -m json.tool

# Expected: JSON response with results array containing prime directives content

# Test add operation
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_to_aya_rag","arguments":{"content":"MCP test document","category":"test"}}}' | python3 /Users/arthurdell/Agent/mcp_servers/aya_postgres_mcp_server.py 2>/dev/null | python3 -m json.tool

# Expected: JSON response with success: true, document_id, chunk_id

# Verify document added
psql -U postgres -d aya_rag -c "SELECT id, content FROM documents WHERE category = 'test' AND content = 'MCP test document';"
# Expected: 1 row

# Cleanup
psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE category = 'test' AND content = 'MCP test document';"
```

**Success Criteria:**
- ✅ Query operation returns results
- ✅ Add operation creates document
- ✅ Embedding generated automatically
- ✅ Cleanup successful

---

## FINAL VERIFICATION MATRIX

### Complete System Health Check

**Execute after all phases complete:**

```bash
# ALPHA Health
curl -s http://localhost:8765/health | grep healthy  # Embedding service
psql -U postgres -c "SELECT COUNT(*) FROM pg_stat_replication;"  # Should be 1
psql -U postgres -d aya_rag -c "SELECT COUNT(*) FROM documents;"  # Data count

# BETA Health
ssh arthurdell@192.168.0.20 "psql -U postgres -d aya_rag -c 'SELECT pg_is_in_recovery();'"  # Should be t
ssh arthurdell@192.168.0.20 "curl -s http://localhost:8765/health | grep healthy"  # Embedding service

# AIR Health (if deployed)
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c 'SELECT COUNT(*) FROM documents;'"
ssh arthurdell@100.103.127.52 "ps aux | grep air_sync_daemon | grep -v grep | wc -l"  # Should be 1

# End-to-End Test
# 1. Insert on ALPHA
psql -U postgres -d aya_rag -c "INSERT INTO documents (content, category) VALUES ('Final E2E test', 'test') RETURNING id;"
# 2. Verify on BETA (within 2 seconds)
sleep 2
ssh arthurdell@192.168.0.20 "psql -U postgres -d aya_rag -c \"SELECT COUNT(*) FROM documents WHERE category = 'test';\""
# 3. Verify on AIR (within 65 seconds)
sleep 65
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c \"SELECT COUNT(*) FROM documents WHERE category = 'test';\""
# 4. Cleanup
psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE category = 'test';"
```

**All Systems Operational Checklist:**

| System | Component | Status | Verification |
|--------|-----------|--------|--------------|
| ALPHA | PostgreSQL | ✅ | Running, primary mode |
| ALPHA | Embedding Service | ✅ | Health check passes |
| ALPHA | Replication | ✅ | 1 active stream |
| BETA | PostgreSQL | ✅ | Running, recovery mode |
| BETA | Replication | ✅ | Lag <1 second |
| BETA | Embedding Service | ✅ | Health check passes |
| AIR | PostgreSQL | ✅ | Running, local mode |
| AIR | Sync Daemon | ✅ | Process running |
| AIR | Write Queue | ✅ | Functional |
| ALL | MCP Servers | ✅ | Query/add working |
| E2E | Data Flow | ✅ | ALPHA→BETA→AIR verified |

---

## RESILIENCE VALIDATION TESTS

### Test 1: Failover Capability
```bash
# Simulate ALPHA failure (DO NOT EXECUTE IN PRODUCTION)
# This test should be documented but executed in controlled environment only

# On BETA - Promote to primary
# pg_ctl promote -D /Volumes/DATA/AYA/data

# Expected result: BETA becomes writable within 60 seconds
# Verify: SELECT pg_is_in_recovery(); -- Should return false
```

**Note:** Failover test requires recovery procedures to be documented separately.

### Test 2: Replication Lag Under Load
```bash
# On ALPHA - Bulk insert
psql -U postgres -d aya_rag -c "INSERT INTO documents (content, category) SELECT 'Load test document ' || generate_series(1, 100), 'test';"

# On BETA - Measure lag immediately
ssh arthurdell@192.168.0.20 "psql -U postgres -d aya_rag -c \"SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;\""

# Expected: <1 second even under load

# Cleanup
psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE category = 'test';"
```

### Test 3: AIR Offline Operation
```bash
# On AIR - Stop sync daemon
ssh arthurdell@100.103.127.52 "kill \$(cat /Users/arthurdell/AYA/services/sync_daemon.pid)"

# On AIR - Queue offline write
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c \"INSERT INTO write_queue (operation, table_name, data) VALUES ('INSERT', 'documents', '{\\\"content\\\": \\\"Offline test\\\", \\\"category\\\": \\\"test\\\"}'::jsonb);\""

# On AIR - Restart sync daemon
ssh arthurdell@100.103.127.52 "cd /Users/arthurdell/AYA/services && nohup python3 air_sync_daemon.py --alpha-host 100.106.113.76 > sync.log 2>&1 & echo \$! > sync_daemon.pid"

# Wait for sync
sleep 65

# Verify synced
ssh arthurdell@100.103.127.52 "psql -U postgres -d aya_rag -c \"SELECT synced FROM write_queue WHERE data->>'content' = 'Offline test';\""
# Expected: synced = t

# Verify on ALPHA
psql -U postgres -d aya_rag -c "SELECT content FROM documents WHERE content = 'Offline test';"
# Expected: Record present

# Cleanup
psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE content = 'Offline test';"
```

---

## EXECUTION TIMELINE

### Optimistic Path (All Components Partially Deployed)
- Phase A: 60 minutes (embedding service + BETA reconnection)
- Phase B: 15 minutes (AIR verification only)
- Phase C: 15 minutes (MCP verification only)
- **Total: 90 minutes**

### Conservative Path (Missing Components)
- Phase A: 75 minutes (including troubleshooting time)
- Phase B: 60 minutes (full AIR deployment)
- Phase C: 45 minutes (full MCP deployment)
- **Total: 180 minutes (3 hours)**

### Critical Path Only (Priority 1 Items)
- Phase A only: 75 minutes
- Achieves: Embedding service operational, BETA replication active, failover capability restored

---

## RISK ASSESSMENT

### High Risk Items
1. **BETA Base Backup Required:** If BETA has no data directory, base backup from ALPHA adds 30 minutes and requires production database access
   - **Mitigation:** Perform during low-usage window, use `--checkpoint=fast` flag

2. **Network Connectivity Issues:** If BETA or AIR unreachable, entire phase blocked
   - **Mitigation:** Verify connectivity before starting execution, document network paths

### Medium Risk Items
3. **Embedding Service Dependencies:** If Python packages missing, installation required
   - **Mitigation:** Pre-verify dependencies before execution

4. **Authentication Failures:** If passwords/SSH keys incorrect, connection failures
   - **Mitigation:** Verify credentials before execution, have backup authentication methods

### Low Risk Items
5. **MCP Server Deployment:** Application layer only, no database impact
   - **Mitigation:** Can be deferred if time-constrained

---

## ROLLBACK PROCEDURES

### Phase A Rollback
**Embedding Service:**
```bash
# Stop service
kill $(cat /Users/arthurdell/AYA/services/embedding_service.pid)
rm /Users/arthurdell/AYA/services/embedding_service.pid
# System returns to pre-execution state (service already down)
```

**BETA Replication:**
```bash
# On BETA - Stop PostgreSQL
sudo launchctl unload /Library/LaunchDaemons/postgresql-18.plist

# On ALPHA - Replication slot remains (no data loss risk)
# No rollback needed on ALPHA side
```

### Phase B Rollback
**AIR Sync Daemon:**
```bash
# On AIR - Stop sync daemon
kill $(cat /Users/arthurdell/AYA/services/sync_daemon.pid)
# AIR returns to offline mode, no data loss
```

### Phase C Rollback
**MCP Servers:** No rollback needed (stateless application layer)

---

## SUCCESS CRITERIA

### Minimum Viable Resilience (Phase A Complete)
- ✅ ALPHA embedding service operational
- ✅ BETA replica streaming from ALPHA
- ✅ Replication lag <1 second
- ✅ Failover capability available (BETA can be promoted)
- ✅ Zero data loss protection active

### Full Resilience (All Phases Complete)
- ✅ All Phase A criteria
- ✅ AIR client synchronizing every 60 seconds
- ✅ AIR offline write queue functional
- ✅ MCP servers operational on all systems
- ✅ End-to-end data flow verified (ALPHA→BETA→AIR)
- ✅ All resilience tests passed

---

## DELIVERABLES

### Phase A Completion Report
- Embedding service status (PID, health check results)
- BETA replication status (lag measurements, connection details)
- Replication test results (INSERT on ALPHA → appearance on BETA timeline)
- All verification checkpoint results

### Phase B Completion Report (if executed)
- AIR system audit findings
- Sync daemon status and log snippets
- Write queue test results
- AIR→ALPHA synchronization verification

### Phase C Completion Report (if executed)
- MCP server deployment status (all 3 systems)
- Integration test results
- Sample query/add operations

### Final System Report
- Complete verification matrix (all checkboxes)
- End-to-end test results
- Resilience test results
- Updated architecture diagram (current state)
- Operational runbook (start/stop/monitor procedures)

---

## NEXT STEPS AFTER COMPLETION

1. **Update Documentation:** Merge this bridging plan results into master documentation
2. **Schedule Failover Test:** Test BETA promotion in controlled environment
3. **Monitoring Setup:** Implement automated health checks and alerting
4. **Backup Strategy:** Configure WAL archiving for point-in-time recovery
5. **Performance Tuning:** Optimize PostgreSQL settings for production workload
6. **Disaster Recovery:** Document full recovery procedures for all failure scenarios

---

## DOCUMENT METADATA

**Plan Status:** READY FOR EXECUTION  
**Approval Required:** Arthur approval before execution  
**Production Impact:** LOW (primarily restart and configuration operations)  
**Estimated Duration:** 90-180 minutes (depending on current deployment state)  
**Critical Path:** Phase A (embedding service + BETA replication)  
**Optional Components:** Phase B (AIR client), Phase C (MCP servers)  

**Execution Authority:** Requires Arthur approval for Phase A. Phases B and C can be deferred.

---

**References:**
- Architecture Specification: `aya_master_2025-10-06_00-10-02.md`
- Current State Audit: `ALPHA_PostgreSQL_Production_Audit_2025-10-08.md`
- Phase 2 Original Report: `phase2_completion_report.md` (BETA setup history)

**Document Version:** 1.0  
**Created:** 2025-10-08 12:15 UTC+4  
**Author:** cursor  
**Review Status:** Pending Arthur approval  

---

*Execution begins upon Arthur's approval. All steps follow bulletproof operator protocol with verification at every stage.*

