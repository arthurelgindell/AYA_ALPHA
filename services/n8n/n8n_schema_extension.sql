-- N8N Schema Extension for aya_rag Database
-- Applied: 2025-10-25
-- Integration: Agent Turbo orchestration with n8n workflow automation

-- Workflow tracking table
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

-- Execution tracking with full audit trail
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

-- Worker coordination and health monitoring
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

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_n8n_workflows_status ON n8n_workflows(status);
CREATE INDEX IF NOT EXISTS idx_n8n_workflows_type ON n8n_workflows(workflow_type);
CREATE INDEX IF NOT EXISTS idx_n8n_workflows_session ON n8n_workflows(agent_session_id);

CREATE INDEX IF NOT EXISTS idx_n8n_executions_workflow ON n8n_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_n8n_executions_status ON n8n_executions(status);
CREATE INDEX IF NOT EXISTS idx_n8n_executions_started ON n8n_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_n8n_executions_task ON n8n_executions(agent_task_id);

CREATE INDEX IF NOT EXISTS idx_n8n_workers_status ON n8n_workers(status);
CREATE INDEX IF NOT EXISTS idx_n8n_workers_heartbeat ON n8n_workers(last_heartbeat DESC);
CREATE INDEX IF NOT EXISTS idx_n8n_workers_node ON n8n_workers(system_node);

-- Materialized views for monitoring
CREATE OR REPLACE VIEW active_n8n_workflows AS
SELECT 
    w.workflow_id,
    w.workflow_name,
    w.workflow_type,
    COUNT(e.id) as total_executions,
    COUNT(CASE WHEN e.success = true THEN 1 END) as successful_executions,
    AVG(e.execution_time_ms) as avg_execution_time_ms,
    MAX(e.finished_at) as last_execution
FROM n8n_workflows w
LEFT JOIN n8n_executions e ON w.workflow_id = e.workflow_id
WHERE w.status = 'active'
GROUP BY w.workflow_id, w.workflow_name, w.workflow_type;

CREATE OR REPLACE VIEW n8n_worker_health AS
SELECT 
    worker_id,
    status,
    last_heartbeat,
    system_node,
    CASE 
        WHEN last_heartbeat > NOW() - INTERVAL '5 minutes' THEN 'healthy'
        WHEN last_heartbeat > NOW() - INTERVAL '15 minutes' THEN 'degraded'
        ELSE 'stale'
    END as health_status
FROM n8n_workers
ORDER BY last_heartbeat DESC;

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON n8n_workflows, n8n_executions, n8n_workers TO n8n_user;

