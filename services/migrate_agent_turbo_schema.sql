-- Agent Turbo PostgreSQL Migration Schema
-- 6 Tables for Multi-Agent Orchestration System
-- Created: 2025-10-26

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Table 1: agent_sessions
-- Tracks all agent sessions with landing context
CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    agent_platform VARCHAR(100) NOT NULL,
    agent_role VARCHAR(100) NOT NULL,
    landing_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);

-- Index for session queries
CREATE INDEX IF NOT EXISTS idx_agent_sessions_platform ON agent_sessions(agent_platform);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_role ON agent_sessions(agent_role);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_status ON agent_sessions(status);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_created ON agent_sessions(created_at DESC);

-- Table 2: agent_tasks
-- Stateful task assignments between agents
CREATE TABLE IF NOT EXISTS agent_tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL,
    task_description TEXT NOT NULL,
    task_parameters JSONB DEFAULT '{}'::jsonb,
    assigned_to VARCHAR(100) NOT NULL,
    task_priority INTEGER DEFAULT 5,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    result JSONB DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);

-- Indexes for task queries
CREATE INDEX IF NOT EXISTS idx_agent_tasks_session ON agent_tasks(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_type ON agent_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_priority ON agent_tasks(task_priority DESC);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_assigned ON agent_tasks(assigned_to);

-- Table 3: agent_knowledge
-- Migrated from SQLite with pgvector support
CREATE TABLE IF NOT EXISTS agent_knowledge (
    knowledge_id VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1024),
    metadata JSONB DEFAULT '{}'::jsonb,
    source VARCHAR(255) DEFAULT 'agent_turbo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

-- Indexes for knowledge queries
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_source ON agent_knowledge(source);
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_created ON agent_knowledge(created_at DESC);
-- pgvector cosine similarity index
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_embedding ON agent_knowledge 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Table 4: agent_actions
-- Complete audit trail of all agent actions
CREATE TABLE IF NOT EXISTS agent_actions (
    action_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    task_id VARCHAR(255) REFERENCES agent_tasks(task_id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL,
    action_description TEXT NOT NULL,
    action_data JSONB DEFAULT '{}'::jsonb,
    agent_platform VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for action queries
CREATE INDEX IF NOT EXISTS idx_agent_actions_session ON agent_actions(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_actions_task ON agent_actions(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_actions_type ON agent_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_agent_actions_created ON agent_actions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_actions_platform ON agent_actions(agent_platform);

-- Table 5: agent_context_cache
-- Landing context snapshots for performance
CREATE TABLE IF NOT EXISTS agent_context_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    context_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for cache expiry cleanup
CREATE INDEX IF NOT EXISTS idx_agent_context_cache_expires ON agent_context_cache(expires_at);

-- Table 6: agent_performance_metrics
-- Track performance metrics for optimization
CREATE TABLE IF NOT EXISTS agent_performance_metrics (
    metric_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for metrics queries
CREATE INDEX IF NOT EXISTS idx_agent_metrics_session ON agent_performance_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_type ON agent_performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_created ON agent_performance_metrics(created_at DESC);

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;

-- Verification query
SELECT 
    'Schema migration complete' as status,
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_name LIKE 'agent_%';
