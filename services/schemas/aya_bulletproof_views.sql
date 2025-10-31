-- AYA Bulletproof Integration Views
-- Database: aya_rag (PostgreSQL 18.0)
-- Purpose: Monitoring and dashboard views for relay coordination
-- Created: 2025-10-31

-- =============================================================================
-- VIEW 1: Current Platform Status
-- =============================================================================

CREATE OR REPLACE VIEW aya_platform_status AS
SELECT 
    'AGENT_SESSIONS' as system,
    COUNT(*) as active_count,
    MAX(last_active) as last_activity
FROM agent_sessions
WHERE status = 'active'
UNION ALL
SELECT 
    'N8N_EXECUTIONS',
    COUNT(*),
    MAX(started_at)
FROM n8n_executions
WHERE finished_at IS NULL
UNION ALL
SELECT 
    'GLADIATOR_RUNS',
    COUNT(*),
    MAX(started_at)
FROM gladiator_training_runs
WHERE status = 'running'
UNION ALL
SELECT 
    'CODE_AUDIT_RUNS',
    COUNT(*),
    MAX(start_time)
FROM code_audit_runs
WHERE status = 'running'
UNION ALL
SELECT
    'RELAY_CYCLES',
    COUNT(*),
    MAX(started_at)
FROM aya_relay_cycles
WHERE completed_at IS NULL
UNION ALL
SELECT
    'INTELLIGENCE_SCOUT',
    COUNT(*),
    MAX(started_at)
FROM intelligence_scout_queue
WHERE status IN ('crawling', 'processing');

COMMENT ON VIEW aya_platform_status IS 'Real-time status of all AYA platform subsystems';

-- =============================================================================
-- VIEW 2: Pending Approvals Dashboard
-- =============================================================================

CREATE OR REPLACE VIEW aya_pending_approvals AS
SELECT 
    a.approval_id,
    a.relay_cycle_id,
    c.cycle_number,
    c.current_phase,
    a.milestone_type,
    a.milestone_description,
    a.requested_at,
    a.requested_by,
    a.impact_analysis,
    EXTRACT(EPOCH FROM (NOW() - a.requested_at))/60 as minutes_pending
FROM aya_milestone_approvals a
JOIN aya_relay_cycles c ON a.relay_cycle_id = c.cycle_id
WHERE a.status = 'pending'
ORDER BY a.requested_at ASC;

COMMENT ON VIEW aya_pending_approvals IS 'Dashboard view of all pending milestone approvals';

-- =============================================================================
-- VIEW 3: Relay Cycle Performance History
-- =============================================================================

CREATE OR REPLACE VIEW aya_relay_performance AS
SELECT 
    c.cycle_id,
    c.cycle_number,
    c.started_at,
    c.completed_at,
    EXTRACT(EPOCH FROM (c.completed_at - c.started_at))/3600 as duration_hours,
    c.improvement_metrics,
    COUNT(DISTINCT e.enhancement_id) as total_enhancements,
    AVG(e.performance_improvement_percent) as avg_performance_gain,
    AVG(e.accuracy_improvement_percent) as avg_accuracy_gain,
    AVG(e.efficiency_gain_percent) as avg_efficiency_gain,
    c.bulletproof_verified,
    CASE 
        WHEN c.alpha_role = 'SOURCE' THEN 'ALPHA'
        ELSE 'BETA'
    END as source_node,
    CASE 
        WHEN c.alpha_role = 'TARGET' THEN 'ALPHA'
        ELSE 'BETA'
    END as target_node
FROM aya_relay_cycles c
LEFT JOIN aya_relay_enhancements e ON c.cycle_id = e.relay_cycle_id
WHERE c.completed_at IS NOT NULL
GROUP BY c.cycle_id, c.cycle_number, c.started_at, c.completed_at, 
         c.improvement_metrics, c.bulletproof_verified, c.alpha_role
ORDER BY c.cycle_number DESC;

COMMENT ON VIEW aya_relay_performance IS 'Historical performance metrics for completed relay cycles';

-- =============================================================================
-- VIEW 4: System Health Dashboard
-- =============================================================================

CREATE OR REPLACE VIEW aya_system_health_dashboard AS
SELECT 
    system_name,
    status,
    last_heartbeat,
    CASE 
        WHEN last_heartbeat < NOW() - INTERVAL '5 minutes' THEN 'STALE'
        WHEN last_heartbeat < NOW() - INTERVAL '2 minutes' THEN 'WARNING'
        ELSE 'OK'
    END as heartbeat_status,
    EXTRACT(EPOCH FROM (NOW() - last_heartbeat))/60 as minutes_since_heartbeat,
    cpu_percent,
    memory_used_gb,
    memory_total_gb,
    ROUND((memory_used_gb / NULLIF(memory_total_gb, 0)) * 100)::numeric(5,2) as memory_percent,
    disk_used_gb,
    disk_total_gb,
    ROUND((disk_used_gb / NULLIF(disk_total_gb, 0)) * 100)::numeric(5,2) as disk_percent,
    active_relay_cycles,
    active_agent_sessions,
    active_n8n_executions,
    active_gladiator_runs,
    network_latency_ms,
    database_size_gb,
    replication_lag_bytes
FROM aya_system_health
ORDER BY system_name;

COMMENT ON VIEW aya_system_health_dashboard IS 'Comprehensive system health monitoring dashboard';

-- =============================================================================
-- VIEW 5: Active Relay Cycle Details
-- =============================================================================

CREATE OR REPLACE VIEW aya_active_relay_details AS
SELECT 
    rc.cycle_id,
    rc.cycle_number,
    rc.current_phase,
    rc.alpha_role,
    rc.beta_role,
    rc.started_at,
    rc.phase_started_at,
    EXTRACT(EPOCH FROM (NOW() - rc.phase_started_at))/60 as minutes_in_phase,
    rc.enhancement_goals,
    rc.phase_transitions,
    (SELECT COUNT(*) FROM aya_verification_chain vc WHERE vc.relay_cycle_id = rc.cycle_id AND vc.verified = true) as verifications_complete,
    (SELECT COUNT(*) FROM aya_verification_chain vc WHERE vc.relay_cycle_id = rc.cycle_id AND vc.verified = false) as verifications_failed,
    (SELECT COUNT(*) FROM aya_milestone_approvals ma WHERE ma.relay_cycle_id = rc.cycle_id AND ma.status = 'pending') as pending_approvals,
    (SELECT COUNT(*) FROM aya_system_operations so WHERE so.relay_cycle_id = rc.cycle_id AND so.status = 'running') as running_operations
FROM aya_relay_cycles rc
WHERE rc.completed_at IS NULL
ORDER BY rc.started_at DESC;

COMMENT ON VIEW aya_active_relay_details IS 'Detailed view of currently active relay cycles';

-- =============================================================================
-- VIEW 6: Audit Trail Summary
-- =============================================================================

CREATE OR REPLACE VIEW aya_audit_summary AS
SELECT 
    DATE(timestamp) as audit_date,
    node,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT relay_cycle_id) as unique_cycles
FROM aya_bulletproof_audit
GROUP BY DATE(timestamp), node, event_type
ORDER BY audit_date DESC, node, event_type;

COMMENT ON VIEW aya_audit_summary IS 'Daily summary of audit trail events';

-- =============================================================================
-- VIEW 7: Enhancement Impact Analysis
-- =============================================================================

CREATE OR REPLACE VIEW aya_enhancement_impact AS
SELECT 
    enhancement_type,
    component_affected,
    COUNT(*) as enhancement_count,
    AVG(performance_improvement_percent) as avg_performance_improvement,
    MAX(performance_improvement_percent) as max_performance_improvement,
    AVG(accuracy_improvement_percent) as avg_accuracy_improvement,
    MAX(accuracy_improvement_percent) as max_accuracy_improvement,
    AVG(efficiency_gain_percent) as avg_efficiency_gain,
    MAX(efficiency_gain_percent) as max_efficiency_gain,
    COUNT(DISTINCT relay_cycle_id) as cycles_involved,
    MIN(applied_at) as first_applied,
    MAX(applied_at) as last_applied
FROM aya_relay_enhancements
GROUP BY enhancement_type, component_affected
ORDER BY avg_performance_improvement DESC NULLS LAST, enhancement_count DESC;

COMMENT ON VIEW aya_enhancement_impact IS 'Impact analysis of enhancements by type and component';

-- =============================================================================
-- VIEW 8: Cross-System Operations Status
-- =============================================================================

CREATE OR REPLACE VIEW aya_operations_status AS
SELECT 
    so.operation_id,
    so.relay_cycle_id,
    rc.cycle_number,
    rc.current_phase as relay_phase,
    so.operation_type,
    so.target_system,
    so.status,
    so.started_at,
    so.completed_at,
    EXTRACT(EPOCH FROM (COALESCE(so.completed_at, NOW()) - so.started_at))/60 as duration_minutes,
    so.bulletproof_verified,
    so.requires_milestone_approval,
    so.milestone_approved,
    as_sess.agent_platform as agent_platform,
    nw.workflow_name as n8n_workflow,
    car.repo_name as code_audit_repo,
    gtr.target_model_name as gladiator_model
FROM aya_system_operations so
JOIN aya_relay_cycles rc ON so.relay_cycle_id = rc.cycle_id
LEFT JOIN agent_sessions as_sess ON so.agent_session_id = as_sess.session_id
LEFT JOIN n8n_workflows nw ON so.n8n_workflow_id = nw.id
LEFT JOIN code_audit_runs car ON so.code_audit_run_id = car.id
LEFT JOIN gladiator_training_runs gtr ON so.gladiator_run_id = gtr.id
ORDER BY so.started_at DESC;

COMMENT ON VIEW aya_operations_status IS 'Status of all cross-system operations linked to relay cycles';

-- =============================================================================
-- COMPLETION
-- =============================================================================

-- Grant read access to views
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
