-- =============================================================================
-- GLADIATOR KNOWLEDGE BASE - REFERENCE DATABASE SCHEMA
-- =============================================================================
-- Project: GLADIATOR Phase 0 - Adversarial AI Cyber Defense Training
-- Target Database: aya_rag (aligned with existing AYA infrastructure)
-- PostgreSQL Version: 18.0
-- Created: 2025-10-10
-- Purpose: Track complete project state, training progress, and validation
-- Standards: Follows AYA documentation pattern with full-text search + JSONB
-- =============================================================================

BEGIN;

-- =============================================================================
-- PART 1: PROJECT METADATA & DOCUMENTATION
-- =============================================================================

-- TABLE 1: gladiator_documentation
-- Stores all project documentation, architecture docs, test plans
CREATE TABLE IF NOT EXISTS gladiator_documentation (
    id SERIAL PRIMARY KEY,
    doc_type VARCHAR(50) NOT NULL,  -- 'architecture', 'test_plan', 'validation', 'status'
    doc_name VARCHAR(200) NOT NULL,
    doc_version VARCHAR(20),
    
    url TEXT,  -- File path or external URL
    title TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    markdown TEXT,
    
    -- MANDATORY: Embedding tracking (AYA Standard)
    embedding_status VARCHAR(20) DEFAULT 'pending',
    embedding_model VARCHAR(100),
    embedding_generated_at TIMESTAMP,
    embedding_chunk_count INTEGER DEFAULT 0,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER,
    status VARCHAR(20) DEFAULT 'draft'  -- 'draft', 'review', 'approved', 'deprecated'
);

CREATE INDEX idx_gladiator_docs_type ON gladiator_documentation(doc_type);
CREATE INDEX idx_gladiator_docs_name ON gladiator_documentation(doc_name);
CREATE INDEX idx_gladiator_docs_status ON gladiator_documentation(status);
CREATE INDEX idx_gladiator_docs_metadata ON gladiator_documentation USING GIN(metadata);
CREATE INDEX idx_gladiator_docs_content_fts ON gladiator_documentation USING GIN(to_tsvector('english', content));

-- =============================================================================
-- PART 2: MODEL REGISTRY
-- =============================================================================

-- TABLE 2: gladiator_models
-- Registry of all models used in training (foundation, red team, blue team)
CREATE TABLE IF NOT EXISTS gladiator_models (
    id SERIAL PRIMARY KEY,
    
    model_name VARCHAR(200) NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL,  -- 'foundation', 'red_team', 'blue_team', 'production'
    model_role VARCHAR(100),  -- 'attack_planning', 'exploit_synthesis', 'threat_detection', etc.
    
    -- Model Source
    source VARCHAR(50) NOT NULL,  -- 'lm_studio', 'huggingface', 'mlx_community', 'custom'
    huggingface_repo TEXT,  -- e.g., 'mlx-community/Llama-3.3-70B-Instruct-4bit'
    model_size_gb NUMERIC(8,2),
    quantization VARCHAR(20),  -- '4bit', '8bit', 'bf16', 'int8'
    
    -- Deployment Details
    deployed_on VARCHAR(50),  -- 'ALPHA', 'BETA', 'AIR'
    deployment_path TEXT,  -- Local filesystem path
    api_endpoint TEXT,  -- e.g., 'http://localhost:1234/v1'
    
    -- Performance Specs
    ram_required_gb INTEGER,
    inference_speed_tok_per_sec NUMERIC(8,2),
    context_window INTEGER,
    
    -- Training Usage
    training_phase VARCHAR(50),  -- 'pre_flight', 'phase_0', 'production'
    instances_count INTEGER DEFAULT 1,  -- How many concurrent instances
    
    -- Status
    status VARCHAR(20) DEFAULT 'planned',  -- 'planned', 'downloading', 'validated', 'active', 'deprecated'
    validated_at TIMESTAMP,
    validation_notes TEXT,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gladiator_models_type ON gladiator_models(model_type);
CREATE INDEX idx_gladiator_models_role ON gladiator_models(model_role);
CREATE INDEX idx_gladiator_models_deployed ON gladiator_models(deployed_on);
CREATE INDEX idx_gladiator_models_status ON gladiator_models(status);
CREATE INDEX idx_gladiator_models_metadata ON gladiator_models USING GIN(metadata);

-- =============================================================================
-- PART 3: TRAINING RUNS & CHECKPOINTS
-- =============================================================================

-- TABLE 3: gladiator_training_runs
-- Tracks each training session (Phase 0 Blue Team fine-tuning)
CREATE TABLE IF NOT EXISTS gladiator_training_runs (
    id SERIAL PRIMARY KEY,
    
    run_name VARCHAR(200) NOT NULL UNIQUE,
    run_type VARCHAR(50) NOT NULL,  -- 'reality_check', 'full_training', 'distillation'
    phase VARCHAR(20) NOT NULL,  -- 'pre_flight', 'phase_0', 'production'
    
    -- Model Being Trained
    base_model_id INTEGER REFERENCES gladiator_models(id),
    target_model_name VARCHAR(200),  -- Name of output model
    
    -- Training Parameters
    training_dataset_size INTEGER,  -- Number of samples
    batch_size INTEGER,
    learning_rate NUMERIC(10,8),
    num_epochs INTEGER,
    num_steps INTEGER,
    
    -- Hardware
    trained_on VARCHAR(50) NOT NULL,  -- 'ALPHA', 'BETA'
    gpu_cores_used INTEGER,
    ram_allocated_gb INTEGER,
    
    -- Progress Tracking
    current_epoch INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 0,
    training_loss NUMERIC(10,6),
    validation_loss NUMERIC(10,6),
    validation_accuracy NUMERIC(5,2),  -- Percentage
    
    -- Time Tracking
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    estimated_completion TIMESTAMP,
    
    -- Results
    final_accuracy NUMERIC(5,2),
    test_accuracy NUMERIC(5,2),  -- On held-out test set
    passed_validation BOOLEAN,
    validation_gate VARCHAR(50),  -- 'gate_3', 'gate_4', etc.
    
    -- Status
    status VARCHAR(50) DEFAULT 'planned',  -- 'planned', 'running', 'completed', 'failed', 'cancelled'
    failure_reason TEXT,
    
    -- Checkpoints
    checkpoint_path TEXT,
    best_checkpoint_path TEXT,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gladiator_training_runs_type ON gladiator_training_runs(run_type);
CREATE INDEX idx_gladiator_training_runs_phase ON gladiator_training_runs(phase);
CREATE INDEX idx_gladiator_training_runs_status ON gladiator_training_runs(status);
CREATE INDEX idx_gladiator_training_runs_started ON gladiator_training_runs(started_at DESC);
CREATE INDEX idx_gladiator_training_runs_metadata ON gladiator_training_runs USING GIN(metadata);

-- TABLE 4: gladiator_training_metrics
-- Time-series metrics for training runs (loss, accuracy over time)
CREATE TABLE IF NOT EXISTS gladiator_training_metrics (
    id SERIAL PRIMARY KEY,
    
    training_run_id INTEGER REFERENCES gladiator_training_runs(id) ON DELETE CASCADE,
    
    epoch INTEGER,
    step INTEGER,
    
    -- Metrics
    training_loss NUMERIC(10,6),
    validation_loss NUMERIC(10,6),
    validation_accuracy NUMERIC(5,2),
    
    -- Hardware Metrics
    gpu_utilization NUMERIC(5,2),  -- Percentage
    ram_usage_gb NUMERIC(8,2),
    gpu_temp_celsius INTEGER,
    
    -- Throughput
    samples_per_second NUMERIC(8,2),
    tokens_per_second NUMERIC(8,2),
    
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_gladiator_training_metrics_run ON gladiator_training_metrics(training_run_id);
CREATE INDEX idx_gladiator_training_metrics_step ON gladiator_training_metrics(step);
CREATE INDEX idx_gladiator_training_metrics_time ON gladiator_training_metrics(measured_at DESC);

-- =============================================================================
-- PART 4: RED TEAM ATTACK PATTERNS
-- =============================================================================

-- TABLE 5: gladiator_attack_patterns
-- Generated attack patterns from Red Team (BETA)
CREATE TABLE IF NOT EXISTS gladiator_attack_patterns (
    id SERIAL PRIMARY KEY,
    
    pattern_id VARCHAR(100) NOT NULL UNIQUE,  -- e.g., 'attack_001234'
    attack_type VARCHAR(100) NOT NULL,  -- 'sql_injection', 'port_scan', 'phishing', etc.
    attack_category VARCHAR(50),  -- 'network', 'web', 'system', 'social', 'apt'
    
    -- Attack Details
    complexity_level INTEGER,  -- 1-10 scale
    mitre_attack_tactic VARCHAR(100),  -- e.g., 'TA0001'
    mitre_attack_technique VARCHAR(100),  -- e.g., 'T1566.001'
    
    -- Generated Content
    payload TEXT,
    description TEXT,
    metadata_json JSONB,  -- Full attack details
    
    -- Generation Details
    generated_by_model_id INTEGER REFERENCES gladiator_models(id),
    generation_method VARCHAR(50),  -- 'llama_70b', 'tinyllama_specialist', 'codellama'
    parent_pattern_id VARCHAR(100),  -- If this is a variant
    variant_number INTEGER,
    
    -- Storage
    storage_path TEXT,  -- Path on BETA:/Volumes/DATA/GLADIATOR/attack_patterns/
    file_size_bytes BIGINT,
    
    -- Classification
    evasion_techniques TEXT[],  -- Array of evasion methods
    target_vulnerabilities TEXT[],
    
    -- Status
    validated BOOLEAN DEFAULT FALSE,
    used_in_training BOOLEAN DEFAULT FALSE,
    training_run_id INTEGER REFERENCES gladiator_training_runs(id),
    
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_gladiator_attack_patterns_type ON gladiator_attack_patterns(attack_type);
CREATE INDEX idx_gladiator_attack_patterns_category ON gladiator_attack_patterns(attack_category);
CREATE INDEX idx_gladiator_attack_patterns_complexity ON gladiator_attack_patterns(complexity_level);
CREATE INDEX idx_gladiator_attack_patterns_mitre ON gladiator_attack_patterns(mitre_attack_technique);
CREATE INDEX idx_gladiator_attack_patterns_model ON gladiator_attack_patterns(generated_by_model_id);
CREATE INDEX idx_gladiator_attack_patterns_used ON gladiator_attack_patterns(used_in_training);
CREATE INDEX idx_gladiator_attack_patterns_time ON gladiator_attack_patterns(generated_at DESC);
CREATE INDEX idx_gladiator_attack_patterns_metadata ON gladiator_attack_patterns USING GIN(metadata_json);

-- TABLE 6: gladiator_attack_generation_stats
-- Daily statistics for Red Team attack generation
CREATE TABLE IF NOT EXISTS gladiator_attack_generation_stats (
    id SERIAL PRIMARY KEY,
    
    stat_date DATE NOT NULL UNIQUE,
    
    -- Generation Counts
    total_patterns_generated INTEGER DEFAULT 0,
    by_category JSONB DEFAULT '{}',  -- {'network': 5000, 'web': 8000, ...}
    by_complexity JSONB DEFAULT '{}',  -- {'1-3': 10000, '4-6': 5000, ...}
    
    -- Model Performance
    llama_70b_patterns INTEGER DEFAULT 0,
    tinyllama_patterns INTEGER DEFAULT 0,
    codellama_patterns INTEGER DEFAULT 0,
    
    -- Storage
    total_storage_bytes BIGINT DEFAULT 0,
    total_storage_gb NUMERIC(10,2),
    
    -- Performance Metrics
    avg_generation_time_ms NUMERIC(10,2),
    patterns_per_hour NUMERIC(10,2),
    
    -- MITRE Coverage
    unique_mitre_tactics INTEGER,
    unique_mitre_techniques INTEGER,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gladiator_attack_gen_stats_date ON gladiator_attack_generation_stats(stat_date DESC);

-- =============================================================================
-- PART 5: VALIDATION & TESTING
-- =============================================================================

-- TABLE 7: gladiator_validation_tests
-- Results of validation gates and tests
CREATE TABLE IF NOT EXISTS gladiator_validation_tests (
    id SERIAL PRIMARY KEY,
    
    test_name VARCHAR(200) NOT NULL,
    test_type VARCHAR(50) NOT NULL,  -- 'pre_flight', 'reality_check', 'gate_validation', 'gauntlet'
    validation_gate VARCHAR(50),  -- 'gate_0', 'gate_1', ..., 'gate_6'
    phase VARCHAR(20),  -- 'pre_flight', 'phase_0', 'production'
    
    -- Test Target
    tested_on VARCHAR(50),  -- 'ALPHA', 'BETA', 'AIR'
    model_id INTEGER REFERENCES gladiator_models(id),
    training_run_id INTEGER REFERENCES gladiator_training_runs(id),
    
    -- Test Parameters
    test_dataset_size INTEGER,
    test_parameters JSONB,
    
    -- Results
    test_result VARCHAR(20) NOT NULL,  -- 'PASS', 'FAIL', 'RUNNING'
    accuracy_percentage NUMERIC(5,2),
    error_rate NUMERIC(5,2),
    pass_threshold NUMERIC(5,2),
    
    -- Performance
    inference_time_ms NUMERIC(10,2),
    throughput_samples_per_sec NUMERIC(10,2),
    
    -- Critical Checks
    self_attack_prevented BOOLEAN,
    feedback_loop_detected BOOLEAN,
    network_throughput_gbps NUMERIC(6,2),
    
    -- Details
    test_output TEXT,
    failure_reason TEXT,
    recommendations TEXT,
    
    -- Decision
    go_no_go_decision VARCHAR(10),  -- 'GO', 'NO-GO', 'PENDING'
    decision_by VARCHAR(100),  -- 'Arthur', 'automated'
    decision_notes TEXT,
    
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_gladiator_validation_tests_type ON gladiator_validation_tests(test_type);
CREATE INDEX idx_gladiator_validation_tests_gate ON gladiator_validation_tests(validation_gate);
CREATE INDEX idx_gladiator_validation_tests_result ON gladiator_validation_tests(test_result);
CREATE INDEX idx_gladiator_validation_tests_decision ON gladiator_validation_tests(go_no_go_decision);
CREATE INDEX idx_gladiator_validation_tests_time ON gladiator_validation_tests(executed_at DESC);

-- =============================================================================
-- PART 6: PHASE MILESTONES & PROJECT STATE
-- =============================================================================

-- TABLE 8: gladiator_phase_milestones
-- Track completion of Phase 0 milestones and gates
CREATE TABLE IF NOT EXISTS gladiator_phase_milestones (
    id SERIAL PRIMARY KEY,
    
    phase VARCHAR(20) NOT NULL,  -- 'pre_flight', 'phase_0', 'production'
    week_number INTEGER,  -- -14, -13, ..., 0 (for Phase 0)
    milestone_name VARCHAR(200) NOT NULL,
    milestone_type VARCHAR(50),  -- 'gate', 'block_completion', 'deliverable'
    
    -- Dependencies
    depends_on INTEGER REFERENCES gladiator_phase_milestones(id),
    blocking BOOLEAN DEFAULT FALSE,  -- If true, must complete before next phase
    
    -- Planned
    planned_start_date DATE,
    planned_end_date DATE,
    estimated_duration_days INTEGER,
    
    -- Actual
    actual_start_date DATE,
    actual_end_date DATE,
    actual_duration_days INTEGER,
    
    -- Status
    status VARCHAR(20) DEFAULT 'planned',  -- 'planned', 'in_progress', 'completed', 'failed', 'cancelled'
    completion_percentage INTEGER DEFAULT 0,
    
    -- Deliverables
    deliverables TEXT[],
    deliverable_paths TEXT[],
    
    -- Validation
    validation_required BOOLEAN DEFAULT FALSE,
    validation_test_id INTEGER REFERENCES gladiator_validation_tests(id),
    validation_passed BOOLEAN,
    
    -- Notes
    notes TEXT,
    blockers TEXT,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gladiator_milestones_phase ON gladiator_phase_milestones(phase);
CREATE INDEX idx_gladiator_milestones_week ON gladiator_phase_milestones(week_number);
CREATE INDEX idx_gladiator_milestones_status ON gladiator_phase_milestones(status);
CREATE INDEX idx_gladiator_milestones_blocking ON gladiator_phase_milestones(blocking);

-- TABLE 9: gladiator_project_state
-- Single source of truth for current project state
CREATE TABLE IF NOT EXISTS gladiator_project_state (
    id SERIAL PRIMARY KEY,
    
    state_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Current Phase
    current_phase VARCHAR(20) NOT NULL,  -- 'pre_flight', 'phase_0', 'production'
    current_week INTEGER,  -- Phase 0 week number
    current_milestone_id INTEGER REFERENCES gladiator_phase_milestones(id),
    
    -- Overall Progress
    phase_0_progress_percentage INTEGER DEFAULT 0,
    days_elapsed INTEGER DEFAULT 0,
    days_remaining INTEGER,
    estimated_completion_date DATE,
    
    -- Red Team Stats
    total_attack_patterns_generated BIGINT DEFAULT 0,
    attack_patterns_target BIGINT DEFAULT 10000000,  -- 10M target
    red_team_progress_percentage INTEGER DEFAULT 0,
    
    -- Blue Team Stats
    training_runs_completed INTEGER DEFAULT 0,
    current_model_accuracy NUMERIC(5,2),
    target_accuracy NUMERIC(5,2) DEFAULT 98.00,
    blue_team_progress_percentage INTEGER DEFAULT 0,
    
    -- Validation Gates
    gates_passed INTEGER DEFAULT 0,
    gates_total INTEGER DEFAULT 7,  -- Gate 0 through Gate 6
    last_gate_passed VARCHAR(50),
    next_gate_due DATE,
    
    -- Infrastructure
    alpha_status VARCHAR(50) DEFAULT 'active',  -- 'active', 'training', 'maintenance', 'offline'
    beta_status VARCHAR(50) DEFAULT 'active',
    air_status VARCHAR(50) DEFAULT 'not_deployed',
    network_throughput_gbps NUMERIC(6,2),
    air_gap_enforced BOOLEAN DEFAULT FALSE,
    
    -- Storage Usage
    alpha_storage_used_gb NUMERIC(10,2),
    beta_storage_used_gb NUMERIC(10,2),
    total_storage_available_gb NUMERIC(10,2),
    
    -- Critical Flags
    production_ready BOOLEAN DEFAULT FALSE,
    self_attack_prevention_validated BOOLEAN DEFAULT FALSE,
    foundation_model_validated BOOLEAN DEFAULT FALSE,
    
    -- Decision Status
    last_go_no_go_decision VARCHAR(10),  -- 'GO', 'NO-GO'
    last_go_no_go_gate VARCHAR(50),
    last_go_no_go_date DATE,
    
    -- Health
    critical_blockers INTEGER DEFAULT 0,
    major_risks INTEGER DEFAULT 0,
    minor_issues INTEGER DEFAULT 0,
    
    metadata JSONB DEFAULT '{}',
    is_current BOOLEAN DEFAULT TRUE  -- Only one row should have TRUE
);

CREATE INDEX idx_gladiator_project_state_current ON gladiator_project_state(is_current);
CREATE INDEX idx_gladiator_project_state_date ON gladiator_project_state(state_date DESC);

-- =============================================================================
-- PART 7: HARDWARE PERFORMANCE TRACKING
-- =============================================================================

-- TABLE 10: gladiator_hardware_performance
-- Track hardware performance during training (extends AYA performance_metrics)
CREATE TABLE IF NOT EXISTS gladiator_hardware_performance (
    id SERIAL PRIMARY KEY,
    
    node_name VARCHAR(50) NOT NULL,  -- 'ALPHA', 'BETA', 'AIR'
    training_run_id INTEGER REFERENCES gladiator_training_runs(id),
    
    -- CPU Metrics
    cpu_utilization_percent NUMERIC(5,2),
    cpu_temp_celsius INTEGER,
    cpu_frequency_mhz INTEGER,
    
    -- GPU Metrics
    gpu_utilization_percent NUMERIC(5,2),
    gpu_temp_celsius INTEGER,
    gpu_memory_used_gb NUMERIC(8,2),
    gpu_memory_total_gb NUMERIC(8,2),
    
    -- RAM Metrics
    ram_used_gb NUMERIC(8,2),
    ram_available_gb NUMERIC(8,2),
    ram_percentage NUMERIC(5,2),
    
    -- Storage Metrics
    storage_used_gb NUMERIC(10,2),
    storage_available_gb NUMERIC(10,2),
    storage_io_read_mbps NUMERIC(10,2),
    storage_io_write_mbps NUMERIC(10,2),
    
    -- Network Metrics
    network_throughput_mbps NUMERIC(10,2),
    network_latency_ms NUMERIC(8,2),
    
    -- Power & Thermal
    power_draw_watts INTEGER,
    thermal_throttling BOOLEAN DEFAULT FALSE,
    
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_gladiator_hw_perf_node ON gladiator_hardware_performance(node_name);
CREATE INDEX idx_gladiator_hw_perf_run ON gladiator_hardware_performance(training_run_id);
CREATE INDEX idx_gladiator_hw_perf_time ON gladiator_hardware_performance(measured_at DESC);

-- =============================================================================
-- PART 8: CHANGE LOG & AUDIT TRAIL
-- =============================================================================

-- TABLE 11: gladiator_change_log
-- Audit trail of all significant changes
CREATE TABLE IF NOT EXISTS gladiator_change_log (
    id SERIAL PRIMARY KEY,
    
    change_type VARCHAR(50) NOT NULL,  -- 'model_update', 'config_change', 'milestone_complete', etc.
    changed_by VARCHAR(100) NOT NULL,  -- 'Arthur', 'cursor', 'automated'
    
    -- Change Details
    entity_type VARCHAR(50),  -- 'model', 'training_run', 'milestone', 'documentation'
    entity_id INTEGER,
    entity_name VARCHAR(200),
    
    -- What Changed
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    
    -- Context
    reason TEXT,
    impact VARCHAR(50),  -- 'low', 'medium', 'high', 'critical'
    
    -- Approval
    requires_approval BOOLEAN DEFAULT FALSE,
    approved BOOLEAN,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_gladiator_change_log_type ON gladiator_change_log(change_type);
CREATE INDEX idx_gladiator_change_log_entity ON gladiator_change_log(entity_type, entity_id);
CREATE INDEX idx_gladiator_change_log_time ON gladiator_change_log(change_timestamp DESC);
CREATE INDEX idx_gladiator_change_log_approval ON gladiator_change_log(requires_approval, approved);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- VIEW: Current project status dashboard
CREATE OR REPLACE VIEW gladiator_status_dashboard AS
SELECT 
    ps.current_phase,
    ps.current_week,
    ps.phase_0_progress_percentage,
    ps.total_attack_patterns_generated,
    ps.attack_patterns_target,
    ps.red_team_progress_percentage,
    ps.current_model_accuracy,
    ps.blue_team_progress_percentage,
    ps.gates_passed,
    ps.gates_total,
    ps.production_ready,
    ps.self_attack_prevention_validated,
    ps.foundation_model_validated,
    ps.critical_blockers,
    ps.state_date as last_updated
FROM gladiator_project_state ps
WHERE ps.is_current = TRUE;

-- VIEW: Latest validation results
CREATE OR REPLACE VIEW gladiator_latest_validations AS
SELECT 
    test_name,
    test_type,
    validation_gate,
    test_result,
    accuracy_percentage,
    go_no_go_decision,
    executed_at
FROM gladiator_validation_tests
WHERE executed_at >= NOW() - INTERVAL '30 days'
ORDER BY executed_at DESC;

-- VIEW: Active training runs
CREATE OR REPLACE VIEW gladiator_active_training AS
SELECT 
    run_name,
    run_type,
    target_model_name,
    current_epoch,
    training_loss,
    validation_accuracy,
    status,
    started_at,
    estimated_completion
FROM gladiator_training_runs
WHERE status IN ('running', 'planned')
ORDER BY started_at DESC;

-- =============================================================================
-- TRIGGERS FOR AUDIT TRAIL
-- =============================================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to relevant tables
CREATE TRIGGER update_gladiator_documentation_updated_at
    BEFORE UPDATE ON gladiator_documentation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gladiator_models_updated_at
    BEFORE UPDATE ON gladiator_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gladiator_training_runs_updated_at
    BEFORE UPDATE ON gladiator_training_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gladiator_milestones_updated_at
    BEFORE UPDATE ON gladiator_phase_milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- INITIAL DATA POPULATION
-- =============================================================================

-- Initialize project state
INSERT INTO gladiator_project_state (
    current_phase,
    current_week,
    current_milestone_id,
    phase_0_progress_percentage,
    attack_patterns_target,
    target_accuracy,
    gates_total,
    alpha_status,
    beta_status,
    air_status,
    air_gap_enforced,
    production_ready,
    self_attack_prevention_validated,
    foundation_model_validated,
    is_current
) VALUES (
    'pre_flight',
    -15,  -- Week -15 (before Phase 0 starts at Week -14)
    NULL,
    0,
    10000000,  -- 10M attack patterns target
    98.00,  -- 98% target accuracy
    7,  -- 7 validation gates (Gate 0 through Gate 6)
    'active',
    'active',
    'not_deployed',
    FALSE,  -- Air-gap not yet enforced
    FALSE,  -- Not production ready
    FALSE,  -- Self-attack prevention not yet validated
    FALSE,  -- Foundation model not yet validated
    TRUE  -- This is the current state
) ON CONFLICT DO NOTHING;

-- Add initial documentation
INSERT INTO gladiator_documentation (
    doc_type,
    doc_name,
    doc_version,
    url,
    title,
    description,
    content,
    word_count,
    status
) VALUES (
    'architecture',
    'GLADIATOR_MASTER_ARCHITECTURE_v2.2.md',
    'v2.2',
    '/Users/arthurdell/Documents/Dropbox/GLADIATOR/GLADIATOR_MASTER_ARCHITECTURE_v2.2.md',
    'GLADIATOR MASTER ARCHITECTURE v2.2',
    'Production-Grade Cyber Defense Platform with Adversarial Training',
    'See file for full content',
    NULL,  -- Will be updated when file is read
    'approved'
),
(
    'test_plan',
    'GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.2.md',
    'v2.2',
    '/Users/arthurdell/Documents/Dropbox/GLADIATOR/GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.2.md',
    'GLADIATOR INFRASTRUCTURE VALIDATION TEST PLAN v2.2',
    'Prove-It-Works Protocol - Zero Assumptions',
    'See file for full content',
    NULL,
    'approved'
) ON CONFLICT DO NOTHING;

COMMIT;

-- =============================================================================
-- SUMMARY & USAGE
-- =============================================================================

-- Table Count: 11 core tables + 3 views
-- Standard: Follows AYA pattern with JSONB metadata, full-text search, timestamps
-- Purpose: Single source of truth for GLADIATOR project state
-- Integration: Links with existing AYA system_nodes, services tables via foreign keys

-- Key Features:
-- 1. Full documentation tracking with full-text search
-- 2. Model registry with validation status
-- 3. Complete training run tracking with time-series metrics
-- 4. Red Team attack pattern database (10M+ patterns)
-- 5. Validation gate tracking with GO/NO-GO decisions
-- 6. Phase 0 milestone tracking (14 weeks)
-- 7. Real-time project state dashboard
-- 8. Hardware performance monitoring
-- 9. Complete audit trail
-- 10. Aligned with AYA infrastructure tables

-- Query Examples:
-- 
-- Get current project status:
--   SELECT * FROM gladiator_status_dashboard;
--
-- Check validation gates:
--   SELECT * FROM gladiator_latest_validations WHERE go_no_go_decision = 'GO';
--
-- Track training progress:
--   SELECT * FROM gladiator_active_training;
--
-- Monitor Red Team generation:
--   SELECT SUM(total_patterns_generated) FROM gladiator_attack_generation_stats;
--
-- Hardware performance:
--   SELECT node_name, AVG(gpu_utilization_percent) 
--   FROM gladiator_hardware_performance 
--   WHERE measured_at >= NOW() - INTERVAL '1 hour'
--   GROUP BY node_name;

-- =============================================================================
-- END OF GLADIATOR SCHEMA
-- =============================================================================

