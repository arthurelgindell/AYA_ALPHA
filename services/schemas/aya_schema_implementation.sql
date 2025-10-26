-- AYA Knowledge Base - Infrastructure State Schema
-- Implementation Date: 2025-10-09
-- Source: AYA_Infrastructure_State_and_Schema_Design_2025-10-09.md
-- Target: aya_rag database

-- =============================================================================
-- PHASE 1: CORE INFRASTRUCTURE TABLES
-- =============================================================================

-- TABLE 1: system_nodes
CREATE TABLE system_nodes (
    id SERIAL PRIMARY KEY,
    node_name VARCHAR(50) NOT NULL UNIQUE,
    node_role VARCHAR(50) NOT NULL,

    -- Hardware Identification
    model_name VARCHAR(100),
    model_identifier VARCHAR(50),
    model_number VARCHAR(50),
    serial_number VARCHAR(50),
    hardware_uuid UUID,

    -- CPU Specifications
    cpu_model VARCHAR(100),
    cpu_architecture VARCHAR(20),
    cpu_cores_total INTEGER,
    cpu_cores_performance INTEGER,
    cpu_cores_efficiency INTEGER,
    cpu_l1_cache_kb INTEGER,
    cpu_l2_cache_mb INTEGER,

    -- GPU Specifications
    gpu_model VARCHAR(100),
    gpu_cores INTEGER,
    gpu_metal_version VARCHAR(20),
    gpu_compute_tflops NUMERIC(6,2),

    -- Memory
    ram_gb INTEGER,
    ram_type VARCHAR(20),
    ram_manufacturer VARCHAR(50),
    ram_bandwidth_gbps INTEGER,

    -- Storage
    storage_internal_tb INTEGER,
    storage_internal_type VARCHAR(50),
    storage_internal_device VARCHAR(100),
    storage_external_tb INTEGER,
    storage_external_device VARCHAR(100),

    -- Operating System
    os_name VARCHAR(50),
    os_version VARCHAR(50),
    os_build VARCHAR(50),
    kernel_version VARCHAR(50),

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    last_verified TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_system_nodes_role ON system_nodes(node_role);
CREATE INDEX idx_system_nodes_status ON system_nodes(status);

-- TABLE 2: network_interfaces
CREATE TABLE network_interfaces (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,

    interface_name VARCHAR(50),
    interface_type VARCHAR(50),
    mac_address MACADDR,

    ipv4_address INET,
    ipv4_netmask INET,
    ipv4_gateway INET,
    ipv6_address INET,
    ipv6_prefix INTEGER,

    connection_speed_mbps INTEGER,
    connection_type VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_network_interfaces_node ON network_interfaces(node_id);
CREATE INDEX idx_network_interfaces_primary ON network_interfaces(is_primary);

-- TABLE 3: software_versions
CREATE TABLE software_versions (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,

    software_name VARCHAR(100) NOT NULL,
    software_version VARCHAR(50),
    software_architecture VARCHAR(20),
    runtime_mode VARCHAR(50),

    install_path TEXT,
    executable_path TEXT,
    compiler VARCHAR(100),

    is_active BOOLEAN DEFAULT TRUE,
    performance_notes TEXT,

    metadata JSONB DEFAULT '{}',
    installed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_software_versions_node ON software_versions(node_id);
CREATE INDEX idx_software_versions_name ON software_versions(software_name);
CREATE UNIQUE INDEX idx_software_unique_active
    ON software_versions(node_id, software_name)
    WHERE is_active = TRUE;

-- TABLE 4: services
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,

    service_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50),
    process_id INTEGER,

    port INTEGER,
    bind_address VARCHAR(50),

    executable_path TEXT,
    config_path TEXT,
    data_path TEXT,
    log_path TEXT,
    pid_file_path TEXT,

    status VARCHAR(20) DEFAULT 'stopped',
    started_at TIMESTAMP,
    uptime_seconds BIGINT,

    auto_start BOOLEAN DEFAULT FALSE,
    auto_restart BOOLEAN DEFAULT FALSE,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_services_node ON services(node_id);
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_services_type ON services(service_type);

-- TABLE 5: replication_status
CREATE TABLE replication_status (
    id SERIAL PRIMARY KEY,
    primary_node_id INTEGER REFERENCES system_nodes(id),
    replica_node_id INTEGER REFERENCES system_nodes(id),

    slot_name VARCHAR(100),
    application_name VARCHAR(100),
    client_address INET,

    state VARCHAR(50),
    sync_state VARCHAR(50),

    replay_lag_ms INTEGER,
    replay_lag_bytes BIGINT,
    write_lag_ms INTEGER,
    flush_lag_ms INTEGER,

    is_active BOOLEAN DEFAULT TRUE,
    last_check TIMESTAMP DEFAULT NOW(),

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_replication_primary ON replication_status(primary_node_id);
CREATE INDEX idx_replication_replica ON replication_status(replica_node_id);
CREATE INDEX idx_replication_active ON replication_status(is_active);


-- =============================================================================
-- PHASE 2: CONFIGURATION & METADATA TABLES
-- =============================================================================

-- TABLE 6: postgresql_configuration
CREATE TABLE postgresql_configuration (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id) ON DELETE CASCADE,

    setting_name VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_unit VARCHAR(20),
    setting_category VARCHAR(100),
    setting_short_desc TEXT,
    context VARCHAR(50),

    is_active BOOLEAN DEFAULT TRUE,
    requires_restart BOOLEAN DEFAULT FALSE,
    pending_value TEXT,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pg_config_node ON postgresql_configuration(node_id);
CREATE INDEX idx_pg_config_name ON postgresql_configuration(setting_name);
CREATE INDEX idx_pg_config_category ON postgresql_configuration(setting_category);
CREATE UNIQUE INDEX idx_pg_config_unique_active
    ON postgresql_configuration(node_id, setting_name)
    WHERE is_active = TRUE;

-- TABLE 7: database_schemas
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
    character_maximum_length INTEGER,

    is_primary_key BOOLEAN DEFAULT FALSE,
    foreign_key_table VARCHAR(100),
    foreign_key_column VARCHAR(100),

    index_name VARCHAR(100),
    index_type VARCHAR(50),
    index_definition TEXT,

    constraint_name VARCHAR(100),
    constraint_type VARCHAR(50),
    constraint_definition TEXT,

    table_size_bytes BIGINT,
    index_size_bytes BIGINT,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_db_schemas_node ON database_schemas(node_id);
CREATE INDEX idx_db_schemas_table ON database_schemas(table_name);
CREATE INDEX idx_db_schemas_database ON database_schemas(database_name);

-- TABLE 8: performance_metrics
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES system_nodes(id),

    metric_category VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value NUMERIC(15,4),
    metric_unit VARCHAR(20),

    test_type VARCHAR(50),
    test_conditions JSONB,

    measured_at TIMESTAMP DEFAULT NOW(),
    measured_by VARCHAR(100),

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_perf_metrics_node ON performance_metrics(node_id);
CREATE INDEX idx_perf_metrics_category ON performance_metrics(metric_category);
CREATE INDEX idx_perf_metrics_name ON performance_metrics(metric_name);
CREATE INDEX idx_perf_metrics_time ON performance_metrics(measured_at DESC);

