-- AYA Bulletproof Architecture Schema
-- Database: aya_rag (PostgreSQL 18.0)
-- Purpose: Immutable audit trail and ALPHA↔BETA relay coordination
-- Created: 2025-10-31

-- =============================================================================
-- CUSTOM TYPES
-- =============================================================================

CREATE TYPE node_role AS ENUM ('SOURCE', 'TARGET', 'IDLE', 'TRANSITION');
CREATE TYPE relay_phase AS ENUM (
    'INIT',        -- Cycle initialization
    'ANALYZE',     -- Source analyzes target capabilities
    'ENHANCE',     -- Source generates improvements to AYA
    'TRANSFER',    -- Deploy enhancements to target
    'VALIDATE',    -- Target validates improvements
    'COMPLETE'     -- Cycle complete, ready for role swap
);

-- =============================================================================
-- TABLE 1: IMMUTABLE AUDIT TRAIL
-- =============================================================================

-- NO DELETES, NO UPDATES - EVER
CREATE TABLE aya_bulletproof_audit (
    event_id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    node VARCHAR(10) NOT NULL CHECK (node IN ('ALPHA', 'BETA', 'GAMMA', 'AIR', 'AYA')),
    event_type VARCHAR(50) NOT NULL,
    
    -- Link to existing systems
    agent_session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    n8n_workflow_id INTEGER REFERENCES n8n_workflows(id),
    gladiator_run_id INTEGER REFERENCES gladiator_training_runs(id),
    jitm_order_id UUID REFERENCES jitm_orders(id),
    
    -- Relay coordination
    relay_cycle_id UUID,
    
    status VARCHAR(20) NOT NULL,
    evidence JSONB NOT NULL,
    
    -- Blockchain integrity
    hash VARCHAR(64) NOT NULL, -- SHA256 of event
    previous_hash VARCHAR(64), -- Chain to previous event
    
    CONSTRAINT no_delete CHECK (false)
);

-- Prevent modifications (BULLETPROOF)
CREATE RULE no_update AS ON UPDATE TO aya_bulletproof_audit DO INSTEAD NOTHING;
CREATE RULE no_delete AS ON DELETE TO aya_bulletproof_audit DO INSTEAD NOTHING;

-- Indexes for chain verification
CREATE INDEX idx_audit_chain ON aya_bulletproof_audit(hash, previous_hash);
CREATE INDEX idx_audit_node_time ON aya_bulletproof_audit(node, timestamp DESC);
CREATE INDEX idx_audit_session ON aya_bulletproof_audit(agent_session_id) 
    WHERE agent_session_id IS NOT NULL;
CREATE INDEX idx_audit_workflow ON aya_bulletproof_audit(n8n_workflow_id) 
    WHERE n8n_workflow_id IS NOT NULL;

-- =============================================================================
-- TABLE 2: ALPHA↔BETA RELAY STATE MACHINE
-- =============================================================================

CREATE TABLE aya_relay_cycles (
    cycle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_number BIGINT GENERATED ALWAYS AS IDENTITY,
    
    alpha_role node_role NOT NULL,
    beta_role node_role NOT NULL,
    current_phase relay_phase NOT NULL,
    
    started_at TIMESTAMPTZ DEFAULT NOW(),
    phase_started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- What's being improved (AYA in its entirety)
    improvement_target VARCHAR(50) NOT NULL DEFAULT 'AYA_SYSTEM',
    enhancement_goals JSONB NOT NULL,
    
    -- Verification tracking
    phase_transitions JSONB DEFAULT '[]'::jsonb,
    verification_checkpoints JSONB DEFAULT '{}'::jsonb,
    
    -- Results
    transfer_manifest JSONB,
    validation_results JSONB,
    improvement_metrics JSONB,
    
    -- Approval gate (semi-autonomous with milestone gates)
    bulletproof_verified BOOLEAN DEFAULT false,
    milestone_approvals JSONB DEFAULT '{}'::jsonb,
    approved_at TIMESTAMPTZ,
    
    -- Enforce valid role pairs
    CONSTRAINT valid_roles CHECK (
        (alpha_role = 'SOURCE' AND beta_role = 'TARGET') OR
        (alpha_role = 'TARGET' AND beta_role = 'SOURCE') OR
        (alpha_role = 'IDLE' AND beta_role = 'IDLE') OR
        (alpha_role = 'TRANSITION' OR beta_role = 'TRANSITION')
    )
);

-- Track phase transitions
CREATE INDEX idx_relay_current ON aya_relay_cycles(current_phase) 
    WHERE completed_at IS NULL;
CREATE INDEX idx_relay_target ON aya_relay_cycles(improvement_target);
CREATE INDEX idx_relay_active ON aya_relay_cycles(started_at DESC) 
    WHERE completed_at IS NULL;

-- =============================================================================
-- TABLE 3: BULLETPROOF VERIFICATION CHAIN
-- =============================================================================

CREATE TABLE aya_verification_chain (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relay_cycle_id UUID REFERENCES aya_relay_cycles(cycle_id),
    
    node VARCHAR(10) NOT NULL,
    phase INTEGER NOT NULL CHECK (phase BETWEEN 1 AND 4),
    phase_name VARCHAR(50) NOT NULL,
    checkpoint VARCHAR(100) NOT NULL,
    
    verified BOOLEAN NOT NULL,
    evidence JSONB NOT NULL,
    verified_at TIMESTAMPTZ DEFAULT NOW(),
    verifier VARCHAR(50) NOT NULL,
    verification_method VARCHAR(100),
    
    -- Milestone gate tracking
    requires_manual_approval BOOLEAN DEFAULT false,
    approval_granted BOOLEAN DEFAULT NULL,
    approved_by VARCHAR(50),
    approved_at TIMESTAMPTZ,
    
    UNIQUE(relay_cycle_id, phase, checkpoint)
);

CREATE INDEX idx_verification_cycle ON aya_verification_chain(relay_cycle_id, phase);
CREATE INDEX idx_verification_pending ON aya_verification_chain(relay_cycle_id) 
    WHERE requires_manual_approval = true AND approval_granted IS NULL;

-- =============================================================================
-- TABLE 4: CROSS-SYSTEM COORDINATION
-- =============================================================================

-- Links bulletproof operations to existing systems
CREATE TABLE aya_system_operations (
    operation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relay_cycle_id UUID REFERENCES aya_relay_cycles(cycle_id),
    
    operation_type VARCHAR(50) NOT NULL,
    target_system VARCHAR(50) NOT NULL,
    
    -- Link to existing system tables
    agent_session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    n8n_workflow_id INTEGER REFERENCES n8n_workflows(id),
    n8n_execution_id INTEGER REFERENCES n8n_executions(id),
    gladiator_run_id INTEGER REFERENCES gladiator_training_runs(id),
    code_audit_run_id INTEGER REFERENCES code_audit_runs(id),
    
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    operation_payload JSONB NOT NULL,
    result JSONB,
    error TEXT,
    
    bulletproof_verified BOOLEAN DEFAULT false,
    
    -- Milestone gate tracking
    requires_milestone_approval BOOLEAN DEFAULT false,
    milestone_approved BOOLEAN DEFAULT NULL,
    milestone_approved_by VARCHAR(50),
    milestone_approved_at TIMESTAMPTZ
);

CREATE INDEX idx_operations_cycle ON aya_system_operations(relay_cycle_id);
CREATE INDEX idx_operations_system ON aya_system_operations(target_system, status);
CREATE INDEX idx_operations_session ON aya_system_operations(agent_session_id) 
    WHERE agent_session_id IS NOT NULL;
CREATE INDEX idx_operations_milestone ON aya_system_operations(relay_cycle_id) 
    WHERE requires_milestone_approval = true AND milestone_approved IS NULL;

-- =============================================================================
-- TABLE 5: GAMMA SUBORDINATION CONTROL (FUTURE)
-- =============================================================================

CREATE TABLE aya_gamma_workloads (
    workload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relay_cycle_id UUID REFERENCES aya_relay_cycles(cycle_id),
    
    authorized_by VARCHAR(10) NOT NULL CHECK (authorized_by IN ('ALPHA', 'BETA')),
    bulletproof_authorized BOOLEAN DEFAULT false,
    authorized_at TIMESTAMPTZ,
    
    workload_type VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    result JSONB,
    
    -- Resource tracking
    compute_hours FLOAT,
    gpu_utilization JSONB,
    memory_peak_gb FLOAT,
    
    -- GAMMA cannot self-authorize (subordination enforcement)
    CONSTRAINT gamma_cannot_self_auth CHECK (authorized_by != 'GAMMA'),
    CONSTRAINT requires_bulletproof_auth CHECK (
        (status != 'running') OR (bulletproof_authorized = true)
    )
);

CREATE INDEX idx_gamma_pending ON aya_gamma_workloads(status) 
    WHERE status = 'pending' AND bulletproof_authorized = true;

-- =============================================================================
-- TABLE 6: SYSTEM HEALTH & MONITORING
-- =============================================================================

CREATE TABLE aya_system_health (
    system_name VARCHAR(10) PRIMARY KEY,
    last_heartbeat TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'unknown',
    
    -- Resource metrics
    cpu_percent FLOAT,
    memory_used_gb FLOAT,
    memory_total_gb FLOAT,
    disk_used_gb FLOAT,
    disk_total_gb FLOAT,
    
    -- Active operations
    active_relay_cycles INTEGER DEFAULT 0,
    active_agent_sessions INTEGER DEFAULT 0,
    active_n8n_executions INTEGER DEFAULT 0,
    active_gladiator_runs INTEGER DEFAULT 0,
    
    -- Network metrics
    network_latency_ms FLOAT,
    
    -- PostgreSQL metrics
    active_connections INTEGER,
    database_size_gb FLOAT,
    replication_lag_bytes BIGINT,
    
    metadata JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABLE 7: RELAY ENHANCEMENT TRACKING
-- =============================================================================

-- Track what AYA system improvements were made in each cycle
CREATE TABLE aya_relay_enhancements (
    enhancement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relay_cycle_id UUID REFERENCES aya_relay_cycles(cycle_id),
    
    enhancement_type VARCHAR(50) NOT NULL,
    component_affected VARCHAR(100) NOT NULL,
    
    before_state JSONB NOT NULL,
    after_state JSONB NOT NULL,
    improvement_delta JSONB NOT NULL,
    
    -- Metrics
    performance_improvement_percent FLOAT,
    accuracy_improvement_percent FLOAT,
    efficiency_gain_percent FLOAT,
    
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    applied_by VARCHAR(10) NOT NULL,
    
    rollback_possible BOOLEAN DEFAULT true,
    rollback_procedure JSONB
);

CREATE INDEX idx_enhancements_cycle ON aya_relay_enhancements(relay_cycle_id);
CREATE INDEX idx_enhancements_type ON aya_relay_enhancements(enhancement_type);
CREATE INDEX idx_enhancements_component ON aya_relay_enhancements(component_affected);

-- =============================================================================
-- TABLE 8: MILESTONE APPROVAL QUEUE
-- =============================================================================

-- Track pending milestone approvals for semi-autonomous operation
CREATE TABLE aya_milestone_approvals (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relay_cycle_id UUID REFERENCES aya_relay_cycles(cycle_id),
    
    milestone_type VARCHAR(50) NOT NULL,
    milestone_description TEXT NOT NULL,
    
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    requested_by VARCHAR(50) NOT NULL,
    
    status VARCHAR(20) DEFAULT 'pending',
    approved_at TIMESTAMPTZ,
    approved_by VARCHAR(50),
    approval_notes TEXT,
    
    context JSONB NOT NULL,
    impact_analysis JSONB
);

CREATE INDEX idx_approvals_pending ON aya_milestone_approvals(status, requested_at) 
    WHERE status = 'pending';
CREATE INDEX idx_approvals_cycle ON aya_milestone_approvals(relay_cycle_id);

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant permissions for application access
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Special permissions for audit table (no updates/deletes even for superuser)
REVOKE UPDATE, DELETE ON aya_bulletproof_audit FROM postgres;

-- =============================================================================
-- COMPLETION
-- =============================================================================

-- Add comment for documentation
COMMENT ON SCHEMA public IS 'AYA Bulletproof Architecture - Immutable audit trail and relay coordination';
