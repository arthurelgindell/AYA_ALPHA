# AYA System State Schema Design
**Date:** 2025-10-09 16:10:00 UTC+4
**Purpose:** Database schema for storing verified system state as source of truth
**Status:** PLANNING PHASE - Assessment Complete

---

## EXECUTIVE SUMMARY

This document defines the database schema for storing the complete, verified state of the AYA Knowledge Base system. This state will be stored **within the PostgreSQL database itself**, creating a self-documenting, queryable system that serves as the single source of truth for all agents and users.

**Design Principles:**
1. **Self-contained:** State stored in the database it describes
2. **Queryable:** SQL-accessible for any agent or tool
3. **Versioned:** Complete change history maintained
4. **Verified:** Only functionally tested states recorded
5. **Agent-agnostic:** Accessible via REST API, SQL, or MCP

---

## CURRENT SYSTEM STATE AUDIT (2025-10-09)

### ALPHA (Primary Server)
**Hardware:**
- Model: Mac Studio (Mac15,14)
- Chip: Apple M3 Ultra
- CPU: 32 cores (24 performance + 8 efficiency)
- GPU: 80 cores (Metal 4)
- RAM: 512 GB
- Disk: 15 TB (99% free)
- Architecture: ARM64

**Network:**
- Primary IP: 192.168.0.80 (LAN)
- Tailscale IP: 100.106.113.76
- Hostname: Not captured yet
- Default gateway: 192.168.0.1

**Software:**
- OS: macOS 15.0 (Darwin 25.0.0)
- Python: 3.9.6 (ARM64 native)
- PostgreSQL: 18.0 (x86_64, Rosetta 2)
- pgvector: 0.8.1
- MLX: 0.29.2 (ARM64 native, Metal-accelerated)
- FastAPI: Latest
- Uvicorn: Latest

**PostgreSQL Configuration (Key Settings):**
- shared_buffers: 128MB (configured 128GB, pending restart)
- effective_cache_size: 384GB ✅ ACTIVE
- work_mem: 64MB ✅ ACTIVE
- maintenance_work_mem: 8GB ✅ ACTIVE
- max_connections: 100 (configured 200, pending restart)
- max_worker_processes: 32 ✅ ACTIVE
- max_parallel_workers: 32 ✅ ACTIVE
- wal_level: replica
- max_wal_senders: 10
- max_replication_slots: 5

**Services:**
- PostgreSQL: RUNNING (PID 1674, started 2025-10-07 12:21:11)
- Embedding Service: RUNNING (PID 65125, port 8765)
- Replication slots: 1 active (beta_slot)

**Database:**
- Name: aya_rag
- Size: 9.4 MB
- Tables: 2 (documents, chunks)
- Documents: 2 rows
- Chunks: 1 row
- Extensions: plpgsql, vector

**Table Schemas:**
```sql
-- documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- chunks table
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(768),
    chunk_index INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);
```

---

### BETA (Replica Server)
**Hardware:**
- Model: Mac Studio (Mac15,14)
- Chip: Apple M3 Ultra
- CPU: 32 cores (24 performance + 8 efficiency)
- GPU: 80 cores (Metal 4)
- RAM: 256 GB
- Disk: 15 TB DATA volume (96% free)
- Architecture: ARM64

**Network:**
- Primary IP: 192.168.0.20 (LAN)
- Tailscale IP: 100.89.227.75
- Hostname: Not captured yet

**Software:**
- OS: macOS (version to be verified)
- Python: 3.9.6 (ARM64 native)
- PostgreSQL: 18.0 (x86_64, Rosetta 2)
- MLX: 0.29.1 (ARM64 native)

**PostgreSQL Configuration (Key Settings):**
- shared_buffers: 128MB (configured 64GB, pending restart)
- effective_cache_size: 192GB ✅ ACTIVE
- work_mem: 64MB ✅ ACTIVE
- maintenance_work_mem: 4GB ✅ ACTIVE
- primary_conninfo: Connected to ALPHA (100.106.113.76)
- primary_slot_name: beta_slot
- hot_standby: on (replica mode)

**Services:**
- PostgreSQL: RUNNING (replica mode)
- Replication: STREAMING from ALPHA
- Data directory: /Volumes/DATA/AYA/data (65 MB)

**Replication Status:**
- Mode: Streaming replication
- Lag: ~2ms
- State: Streaming
- Sync state: async

---

### AIR (Mobile Client)
**Status:** NOT ACCESSIBLE
- Network: Reachable via Tailscale (100.103.127.52)
- SSH: BLOCKED (host key verification)
- Deployment: DEFERRED to Phase 3

---

## PROPOSED DATABASE SCHEMA

### Schema Design Philosophy

**Core Principles:**
1. **Normalized data structure** - Avoid duplication
2. **Temporal tracking** - Record when states change
3. **Queryable relationships** - Foreign keys for navigation
4. **JSON flexibility** - Use JSONB for complex/variable data
5. **Immutable history** - Never delete historical records

---

### TABLE 1: `system_nodes`
**Purpose:** Physical systems in the AYA infrastructure

```sql
CREATE TABLE system_nodes (
    id SERIAL PRIMARY KEY,
    node_name VARCHAR(50) NOT NULL UNIQUE,  -- 'ALPHA', 'BETA', 'AIR'
    node_role VARCHAR(50) NOT NULL,         -- 'primary', 'replica', 'client'
    hardware_model VARCHAR(100),            -- 'Mac Studio Mac15,14'
    cpu_model VARCHAR(100),                 -- 'Apple M3 Ultra'
    cpu_cores INTEGER,                      -- 32
    cpu_performance_cores INTEGER,          -- 24
    cpu_efficiency_cores INTEGER,           -- 8
    gpu_model VARCHAR(100),                 -- 'Apple M3 Ultra GPU'
    gpu_cores INTEGER,                      -- 80
    ram_gb INTEGER,                         -- 512
    disk_tb INTEGER,                        -- 15
    architecture VARCHAR(20),               -- 'ARM64', 'x86_64'
    os_name VARCHAR(50),                    -- 'macOS'
    os_version VARCHAR(50),                 -- '15.0 (Darwin 25.0.0)'
    serial_number VARCHAR(50),              -- Hardware serial
    status VARCHAR(20) DEFAULT 'active',    -- 'active', 'inactive', 'maintenance'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_system_nodes_role ON system_nodes(node_role);
CREATE INDEX idx_system_nodes_status ON system_nodes(node_status);
```

---

### TABLE 2: `network_interfaces`
**Purpose:** Network configuration for each node

```sql
CREATE TABLE network_interfaces (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,
    interface_name VARCHAR(50),             -- 'en0', 'utun4'
    interface_type VARCHAR(50),             -- 'ethernet', 'vpn', 'loopback'
    ip_address INET,                        -- '192.168.0.80'
    netmask INET,                           -- '255.255.255.0'
    gateway INET,                           -- '192.168.0.1'
    is_primary BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',    -- 'active', 'inactive'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_network_interfaces_node ON network_interfaces(node_id);
CREATE INDEX idx_network_interfaces_primary ON network_interfaces(is_primary);
```

---

### TABLE 3: `software_versions`
**Purpose:** Track all software versions on each node

```sql
CREATE TABLE software_versions (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,
    software_name VARCHAR(100) NOT NULL,    -- 'PostgreSQL', 'Python', 'MLX'
    software_version VARCHAR(50),           -- '18.0', '3.9.6'
    architecture VARCHAR(20),               -- 'ARM64', 'x86_64', 'Universal'
    runtime_mode VARCHAR(50),               -- 'native', 'Rosetta 2'
    install_path TEXT,                      -- '/Library/PostgreSQL/18'
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',            -- Additional version details
    installed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_software_versions_node ON software_versions(node_id);
CREATE INDEX idx_software_versions_name ON software_versions(software_name);
CREATE INDEX idx_software_versions_active ON software_versions(is_active);

-- Unique constraint: one active version per software per node
CREATE UNIQUE INDEX idx_software_unique_active
    ON software_versions(node_id, software_name)
    WHERE is_active = TRUE;
```

---

### TABLE 4: `postgresql_configuration`
**Purpose:** PostgreSQL settings for each database

```sql
CREATE TABLE postgresql_configuration (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,
    setting_name VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_unit VARCHAR(20),               -- 'kB', '8kB', 'ms', etc.
    setting_category VARCHAR(100),          -- 'Resource Usage / Memory'
    context VARCHAR(50),                    -- 'user', 'sighup', 'postmaster'
    is_active BOOLEAN DEFAULT TRUE,         -- Current vs pending restart
    requires_restart BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_pg_config_node ON postgresql_configuration(node_id);
CREATE INDEX idx_pg_config_name ON postgresql_configuration(setting_name);
CREATE INDEX idx_pg_config_active ON postgresql_configuration(is_active);

-- Unique constraint: one active setting per name per node
CREATE UNIQUE INDEX idx_pg_config_unique_active
    ON postgresql_configuration(node_id, setting_name)
    WHERE is_active = TRUE;
```

---

### TABLE 5: `services`
**Purpose:** Track running services on each node

```sql
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,     -- 'PostgreSQL', 'Embedding Service'
    service_type VARCHAR(50),               -- 'database', 'api', 'daemon'
    process_id INTEGER,                     -- PID
    port INTEGER,                           -- Listening port
    bind_address VARCHAR(50),               -- '0.0.0.0', 'localhost'
    executable_path TEXT,                   -- Full path to binary
    config_path TEXT,                       -- Configuration file path
    data_path TEXT,                         -- Data directory
    status VARCHAR(20) DEFAULT 'stopped',   -- 'running', 'stopped', 'failed'
    started_at TIMESTAMP,
    auto_start BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',            -- Service-specific config
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_services_node ON services(node_id);
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_services_type ON services(service_type);
```

---

### TABLE 6: `replication_status`
**Purpose:** Track replication relationships and health

```sql
CREATE TABLE replication_status (
    id SERIAL PRIMARY KEY,
    primary_node_id INTEGER REFERENCES system_nodes(id),
    replica_node_id INTEGER REFERENCES system_nodes(id),
    slot_name VARCHAR(100),                 -- 'beta_slot'
    application_name VARCHAR(100),          -- 'walreceiver'
    state VARCHAR(50),                      -- 'streaming', 'catchup', 'stopped'
    sync_state VARCHAR(50),                 -- 'async', 'sync'
    replay_lag_ms INTEGER,                  -- Lag in milliseconds
    bytes_lag BIGINT,                       -- Bytes behind
    is_active BOOLEAN DEFAULT TRUE,
    last_check TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_replication_primary ON replication_status(primary_node_id);
CREATE INDEX idx_replication_replica ON replication_status(replica_node_id);
CREATE INDEX idx_replication_active ON replication_status(is_active);
```

---

### TABLE 7: `database_schemas`
**Purpose:** Track database schema definitions

```sql
CREATE TABLE database_schemas (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id),
    database_name VARCHAR(100) NOT NULL,
    schema_name VARCHAR(100) DEFAULT 'public',
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    data_type VARCHAR(100),
    is_nullable BOOLEAN,
    column_default TEXT,
    is_primary_key BOOLEAN DEFAULT FALSE,
    foreign_key_table VARCHAR(100),
    foreign_key_column VARCHAR(100),
    index_name VARCHAR(100),
    index_type VARCHAR(50),                 -- 'btree', 'ivfflat', 'hnsw'
    metadata JSONB DEFAULT '{}',            -- Full DDL, constraints, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_db_schemas_node ON database_schemas(node_id);
CREATE INDEX idx_db_schemas_table ON database_schemas(table_name);
```

---

### TABLE 8: `performance_metrics`
**Purpose:** Store performance test results over time

```sql
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id),
    metric_category VARCHAR(50),            -- 'database', 'embedding', 'replication'
    metric_name VARCHAR(100),               -- 'simple_query_time', 'embedding_generation'
    metric_value NUMERIC,                   -- Measured value
    metric_unit VARCHAR(20),                -- 'ms', 'MB', 'records/sec'
    test_type VARCHAR(50),                  -- 'load_test', 'health_check'
    metadata JSONB DEFAULT '{}',            -- Test details, conditions
    measured_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_perf_metrics_node ON performance_metrics(node_id);
CREATE INDEX idx_perf_metrics_category ON performance_metrics(metric_category);
CREATE INDEX idx_perf_metrics_time ON performance_metrics(measured_at DESC);

-- Hypertable for time-series (if using TimescaleDB extension)
-- SELECT create_hypertable('performance_metrics', 'measured_at');
```

---

### TABLE 9: `system_state_snapshots`
**Purpose:** Point-in-time snapshots of complete system state

```sql
CREATE TABLE system_state_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_name VARCHAR(100) NOT NULL UNIQUE,
    snapshot_type VARCHAR(50),              -- 'production', 'verified', 'baseline'
    description TEXT,
    verification_status VARCHAR(50),        -- 'verified', 'partial', 'failed'
    tests_passed INTEGER,
    tests_failed INTEGER,
    state_json JSONB NOT NULL,              -- Complete state as JSON
    created_by VARCHAR(100),                -- 'Claude Code', 'Arthur Dell'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_snapshots_type ON system_state_snapshots(snapshot_type);
CREATE INDEX idx_snapshots_status ON system_state_snapshots(verification_status);
CREATE INDEX idx_snapshots_created ON system_state_snapshots(created_at DESC);
```

---

### TABLE 10: `change_log`
**Purpose:** Audit trail of all system changes

```sql
CREATE TABLE change_log (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id),
    change_type VARCHAR(50),                -- 'configuration', 'service', 'schema'
    change_category VARCHAR(50),            -- 'optimization', 'restoration', 'deployment'
    table_affected VARCHAR(100),            -- Which table was modified
    record_id INTEGER,                      -- ID of affected record
    change_description TEXT NOT NULL,
    old_value JSONB,                        -- Previous state
    new_value JSONB,                        -- New state
    changed_by VARCHAR(100),                -- 'Claude Code', 'Arthur Dell', 'system'
    change_reason TEXT,
    verification_status VARCHAR(50),        -- 'verified', 'pending', 'failed'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_change_log_node ON change_log(node_id);
CREATE INDEX idx_change_log_type ON change_log(change_type);
CREATE INDEX idx_change_log_created ON change_log(created_at DESC);
CREATE INDEX idx_change_log_by ON change_log(changed_by);
```

---

### TABLE 11: `documentation_files`
**Purpose:** Track documentation files and their sync status

```sql
CREATE TABLE documentation_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    file_hash VARCHAR(64),                  -- SHA-256 for integrity
    category VARCHAR(50),                   -- 'master_plan', 'verification', 'audit'
    description TEXT,
    content TEXT,                           -- Full markdown content
    sync_locations JSONB DEFAULT '[]',      -- Array of synced locations
    is_latest BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_docs_name ON documentation_files(file_name);
CREATE INDEX idx_docs_category ON documentation_files(category);
CREATE INDEX idx_docs_latest ON documentation_files(is_latest);
CREATE INDEX idx_docs_updated ON documentation_files(updated_at DESC);
```

---

## VIEWS FOR CONVENIENT QUERYING

### VIEW 1: `v_system_overview`
```sql
CREATE VIEW v_system_overview AS
SELECT
    n.node_name,
    n.node_role,
    n.cpu_model,
    n.cpu_cores,
    n.gpu_cores,
    n.ram_gb,
    n.disk_tb,
    n.architecture,
    n.status,
    ni.ip_address AS primary_ip,
    COUNT(DISTINCT s.id) AS running_services,
    COUNT(DISTINCT sv.id) AS installed_software
FROM system_nodes n
LEFT JOIN network_interfaces ni ON n.id = ni.node_id AND ni.is_primary = TRUE
LEFT JOIN services s ON n.id = s.node_id AND s.status = 'running'
LEFT JOIN software_versions sv ON n.id = sv.node_id AND sv.is_active = TRUE
GROUP BY n.id, ni.ip_address;
```

### VIEW 2: `v_replication_health`
```sql
CREATE VIEW v_replication_health AS
SELECT
    pn.node_name AS primary_node,
    rn.node_name AS replica_node,
    rs.state,
    rs.sync_state,
    rs.replay_lag_ms,
    rs.is_active,
    rs.last_check
FROM replication_status rs
JOIN system_nodes pn ON rs.primary_node_id = pn.id
JOIN system_nodes rn ON rs.replica_node_id = rn.id
WHERE rs.is_active = TRUE;
```

### VIEW 3: `v_service_status`
```sql
CREATE VIEW v_service_status AS
SELECT
    n.node_name,
    s.service_name,
    s.service_type,
    s.status,
    s.port,
    s.started_at,
    EXTRACT(EPOCH FROM (NOW() - s.started_at))/3600 AS uptime_hours
FROM services s
JOIN system_nodes n ON s.node_id = n.id
ORDER BY n.node_name, s.service_name;
```

### VIEW 4: `v_current_configuration`
```sql
CREATE VIEW v_current_configuration AS
SELECT
    n.node_name,
    pc.setting_name,
    pc.setting_value,
    pc.setting_unit,
    pc.is_active,
    pc.requires_restart
FROM postgresql_configuration pc
JOIN system_nodes n ON pc.node_id = n.id
WHERE pc.is_active = TRUE
ORDER BY n.node_name, pc.setting_category, pc.setting_name;
```

---

## IMPLEMENTATION PLAN

### Phase 1: Schema Creation (15 minutes)
1. Create all 11 tables
2. Create indexes
3. Create views
4. Verify schema integrity

### Phase 2: Initial Data Population (30 minutes)
1. Insert system_nodes (ALPHA, BETA, AIR)
2. Insert network_interfaces
3. Insert software_versions
4. Insert postgresql_configuration (from current settings)
5. Insert services (current running services)
6. Insert replication_status
7. Insert database_schemas (from information_schema)

### Phase 3: Create Snapshot (15 minutes)
1. Generate complete state JSON
2. Insert into system_state_snapshots
3. Mark as "Production Verified 2025-10-09"
4. Run verification queries

### Phase 4: Documentation & Testing (20 minutes)
1. Create query examples
2. Test all views
3. Verify data integrity
4. Document access methods (REST API, SQL, MCP)

**Total estimated time:** 80 minutes (1 hour 20 minutes)

---

## QUERY EXAMPLES

### Get current system state
```sql
SELECT * FROM v_system_overview;
```

### Check replication health
```sql
SELECT * FROM v_replication_health;
```

### See all running services
```sql
SELECT * FROM v_service_status WHERE status = 'running';
```

### Get performance history for last 24 hours
```sql
SELECT
    n.node_name,
    pm.metric_name,
    AVG(pm.metric_value) AS avg_value,
    MIN(pm.metric_value) AS min_value,
    MAX(pm.metric_value) AS max_value,
    pm.metric_unit
FROM performance_metrics pm
JOIN system_nodes n ON pm.node_id = n.id
WHERE pm.measured_at > NOW() - INTERVAL '24 hours'
GROUP BY n.node_name, pm.metric_name, pm.metric_unit
ORDER BY n.node_name, pm.metric_name;
```

### Get latest snapshot
```sql
SELECT
    snapshot_name,
    verification_status,
    tests_passed,
    tests_failed,
    created_at
FROM system_state_snapshots
ORDER BY created_at DESC
LIMIT 1;
```

### Get change history for a node
```sql
SELECT
    cl.change_type,
    cl.change_description,
    cl.changed_by,
    cl.created_at
FROM change_log cl
JOIN system_nodes n ON cl.node_id = n.id
WHERE n.node_name = 'ALPHA'
ORDER BY cl.created_at DESC
LIMIT 20;
```

---

## ACCESS METHODS

### 1. Direct SQL (PostgreSQL native)
```bash
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c \
  "SELECT * FROM v_system_overview;"
```

### 2. REST API (Future Phase 4)
```bash
curl http://localhost:8080/api/v1/system/state
curl http://localhost:8080/api/v1/replication/health
curl http://localhost:8080/api/v1/services/status
```

### 3. MCP Server (Future Phase 4, Claude/Cursor only)
```json
{
  "method": "tools/call",
  "params": {
    "name": "query_system_state",
    "arguments": {}
  }
}
```

---

## DATA RETENTION & ARCHIVAL

**Performance Metrics:**
- Retain raw data: 30 days
- Aggregate to hourly: 1 year
- Aggregate to daily: 5 years

**Change Log:**
- Retain all: Indefinite (audit requirement)
- Index cleanup: Older than 1 year moves to archive

**Snapshots:**
- Verified snapshots: Keep all
- Automated snapshots: Keep latest 10

---

## BENEFITS

1. **Self-Documenting:** System describes itself via SQL
2. **Agent-Accessible:** Any tool with PostgreSQL access can query state
3. **Version Controlled:** Complete change history
4. **Performance Tracked:** Metrics over time
5. **Compliance Ready:** Full audit trail
6. **Recovery Enabled:** Point-in-time snapshots
7. **Truth Single Source:** No conflicting documentation

---

## NEXT STEPS

**PLANNING PHASE (Current):**
- [x] Audit current system state
- [x] Design database schema
- [ ] Review with Arthur for approval
- [ ] Refine schema based on feedback

**IMPLEMENTATION PHASE (After approval):**
- [ ] Create tables and indexes
- [ ] Create views
- [ ] Populate initial data
- [ ] Create baseline snapshot
- [ ] Test queries
- [ ] Document access patterns
- [ ] Sync documentation

---

**Document Status:** PLANNING - Awaiting Review
**Created by:** Claude Code (Anthropic)
**Date:** 2025-10-09 16:10:00 UTC+4
**Next Review:** Pending Arthur approval
