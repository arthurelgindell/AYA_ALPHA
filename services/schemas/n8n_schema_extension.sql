-- N8N Schema Extension for AYA Infrastructure
-- Database: aya_rag (PostgreSQL 18.0)
-- Purpose: Integrate n8n workflow automation with Agent Turbo orchestration
-- Created: 2025-10-25

-- =============================================================================
-- N8N WORKFLOW TRACKING
-- =============================================================================

-- Table: n8n_workflows
-- Purpose: Track all n8n workflows and their lifecycle
CREATE TABLE IF NOT EXISTS n8n_workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    agent_session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE n8n_workflows IS 'n8n workflow definitions and lifecycle tracking';
COMMENT ON COLUMN n8n_workflows.workflow_id IS 'Unique n8n workflow identifier';
COMMENT ON COLUMN n8n_workflows.agent_session_id IS 'Links workflow to Agent Turbo session for orchestration';
COMMENT ON COLUMN n8n_workflows.metadata IS 'Workflow configuration, triggers, nodes, and custom data';

-- =============================================================================
-- N8N EXECUTION TRACKING
-- =============================================================================

-- Table: n8n_executions
-- Purpose: Log every workflow execution with timing and results
CREATE TABLE IF NOT EXISTS n8n_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_id VARCHAR(100) REFERENCES n8n_workflows(workflow_id),
    status VARCHAR(20),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    agent_task_id VARCHAR(100) REFERENCES agent_tasks(task_id),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE n8n_executions IS 'Complete execution log for all workflow runs';
COMMENT ON COLUMN n8n_executions.execution_id IS 'Unique execution identifier from n8n';
COMMENT ON COLUMN n8n_executions.agent_task_id IS 'Links execution to Agent Turbo task for tracking';
COMMENT ON COLUMN n8n_executions.metadata IS 'Execution data: inputs, outputs, node results, errors';

-- =============================================================================
-- N8N WORKER COORDINATION
-- =============================================================================

-- Table: n8n_workers
-- Purpose: Track distributed worker containers and their status
CREATE TABLE IF NOT EXISTS n8n_workers (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(100) UNIQUE NOT NULL,
    worker_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'idle',
    assigned_workflow VARCHAR(100),
    last_heartbeat TIMESTAMP,
    system_node VARCHAR(50),
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE n8n_workers IS 'Distributed n8n worker containers for scaling';
COMMENT ON COLUMN n8n_workers.worker_id IS 'Unique worker identifier (container name or hostname)';
COMMENT ON COLUMN n8n_workers.system_node IS 'Physical system (ALPHA/BETA) where worker runs';
COMMENT ON COLUMN n8n_workers.last_heartbeat IS 'Last health check timestamp for monitoring';

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_n8n_workflows_status ON n8n_workflows(status);
CREATE INDEX IF NOT EXISTS idx_n8n_workflows_session ON n8n_workflows(agent_session_id);
CREATE INDEX IF NOT EXISTS idx_n8n_workflows_type ON n8n_workflows(workflow_type);

CREATE INDEX IF NOT EXISTS idx_n8n_executions_workflow ON n8n_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_n8n_executions_status ON n8n_executions(status);
CREATE INDEX IF NOT EXISTS idx_n8n_executions_started ON n8n_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_n8n_executions_task ON n8n_executions(agent_task_id);

CREATE INDEX IF NOT EXISTS idx_n8n_workers_status ON n8n_workers(status);
CREATE INDEX IF NOT EXISTS idx_n8n_workers_heartbeat ON n8n_workers(last_heartbeat DESC);
CREATE INDEX IF NOT EXISTS idx_n8n_workers_node ON n8n_workers(system_node);

-- =============================================================================
-- INTEGRATION VIEWS
-- =============================================================================

-- View: n8n_active_workflows
-- Purpose: Quick view of all active workflows with recent execution stats
CREATE OR REPLACE VIEW n8n_active_workflows AS
SELECT 
    w.workflow_id,
    w.workflow_name,
    w.workflow_type,
    w.status,
    w.agent_session_id,
    COUNT(e.id) as total_executions,
    SUM(CASE WHEN e.success = true THEN 1 ELSE 0 END) as successful_executions,
    AVG(e.execution_time_ms) as avg_execution_time_ms,
    MAX(e.finished_at) as last_execution
FROM n8n_workflows w
LEFT JOIN n8n_executions e ON w.workflow_id = e.workflow_id
WHERE w.status = 'active'
GROUP BY w.workflow_id, w.workflow_name, w.workflow_type, w.status, w.agent_session_id;

COMMENT ON VIEW n8n_active_workflows IS 'Active workflows with execution statistics';

-- View: n8n_worker_health
-- Purpose: Monitor worker health and activity
CREATE OR REPLACE VIEW n8n_worker_health AS
SELECT 
    worker_id,
    worker_type,
    status,
    system_node,
    last_heartbeat,
    CASE 
        WHEN last_heartbeat > NOW() - INTERVAL '5 minutes' THEN 'healthy'
        WHEN last_heartbeat > NOW() - INTERVAL '15 minutes' THEN 'warning'
        ELSE 'stale'
    END as health_status,
    assigned_workflow
FROM n8n_workers
ORDER BY last_heartbeat DESC;

COMMENT ON VIEW n8n_worker_health IS 'Worker health monitoring with status indicators';

-- =============================================================================
-- VERIFICATION QUERY
-- =============================================================================

-- Verify schema was applied successfully
DO $$
BEGIN
    RAISE NOTICE 'N8N Schema Extension Applied Successfully';
    RAISE NOTICE 'Tables Created: n8n_workflows, n8n_executions, n8n_workers';
    RAISE NOTICE 'Views Created: n8n_active_workflows, n8n_worker_health';
    RAISE NOTICE 'Integration: Linked to agent_sessions and agent_tasks';
END $$;

