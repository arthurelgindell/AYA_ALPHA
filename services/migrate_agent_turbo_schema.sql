-- ====================================================================
-- AYA Agent Turbo PostgreSQL Schema Migration
-- Migration from SQLite to PostgreSQL with Agent Orchestration
-- Date: 2025-10-14
-- Prime Directives Compliance: MANDATORY
-- ====================================================================

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS agent_actions CASCADE;
DROP TABLE IF EXISTS agent_tasks CASCADE;
DROP TABLE IF EXISTS agent_sessions CASCADE;
DROP TABLE IF EXISTS agent_knowledge CASCADE;
DROP TABLE IF EXISTS agent_context_cache CASCADE;

-- ====================================================================
-- TABLE 1: agent_sessions
-- Purpose: Track all agent sessions across platforms
-- ====================================================================
CREATE TABLE agent_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    agent_platform VARCHAR(50) NOT NULL,  -- 'claude_code', 'openai', 'gemini', etc.
    agent_role VARCHAR(50) NOT NULL,      -- 'planner', 'auditor', 'executor', 'validator'
    parent_session_id VARCHAR(100),       -- For delegation chains
    
    -- Landing context
    context_snapshot_id INTEGER REFERENCES system_state_snapshots(id),
    landing_context JSONB NOT NULL,       -- Complete system state at init
    
    -- Session lifecycle
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'idle', 'completed', 'failed'
    
    -- Performance tracking
    tokens_used INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    
    metadata JSONB DEFAULT '{}'
);

-- Indexes for agent_sessions
CREATE INDEX idx_agent_sessions_platform ON agent_sessions(agent_platform);
CREATE INDEX idx_agent_sessions_role ON agent_sessions(agent_role);
CREATE INDEX idx_agent_sessions_status ON agent_sessions(status);
CREATE INDEX idx_agent_sessions_parent ON agent_sessions(parent_session_id);
CREATE INDEX idx_agent_sessions_created ON agent_sessions(created_at DESC);

-- ====================================================================
-- TABLE 2: agent_tasks
-- Purpose: Stateful task assignments for multi-agent coordination
-- ====================================================================
CREATE TABLE agent_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    
    -- Task definition
    task_type VARCHAR(50) NOT NULL,       -- 'code_review', 'implementation', 'testing', etc.
    task_description TEXT NOT NULL,
    task_priority INTEGER DEFAULT 5,      -- 1-10
    
    -- Assignment
    assigned_by VARCHAR(100),             -- Planner session_id
    assigned_to_role VARCHAR(50),         -- Target agent role
    assigned_to_platform VARCHAR(50),     -- Preferred platform
    
    -- Execution context
    required_context JSONB DEFAULT '{}',  -- Specific context needed
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    
    -- Lifecycle
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'assigned', 'in_progress', 'completed', 'failed', 'blocked'
    
    -- Dependencies
    depends_on_tasks TEXT[],              -- Array of task_ids
    blocks_tasks TEXT[],
    
    -- Progress tracking
    progress_percentage INTEGER DEFAULT 0,
    current_step TEXT,
    error_message TEXT,
    
    metadata JSONB DEFAULT '{}'
);

-- Indexes for agent_tasks
CREATE INDEX idx_agent_tasks_session ON agent_tasks(session_id);
CREATE INDEX idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX idx_agent_tasks_type ON agent_tasks(task_type);
CREATE INDEX idx_agent_tasks_assigned_by ON agent_tasks(assigned_by);
CREATE INDEX idx_agent_tasks_assigned_to_role ON agent_tasks(assigned_to_role);
CREATE INDEX idx_agent_tasks_priority ON agent_tasks(task_priority DESC);
CREATE INDEX idx_agent_tasks_created ON agent_tasks(created_at DESC);

-- ====================================================================
-- TABLE 3: agent_knowledge
-- Purpose: Migrated from SQLite with PostgreSQL pgvector optimizations
-- ====================================================================
CREATE TABLE agent_knowledge (
    id SERIAL PRIMARY KEY,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),                -- pgvector for semantic search
    
    -- Source tracking
    source_session VARCHAR(100),
    source_agent_platform VARCHAR(50),
    
    -- Classification
    knowledge_type VARCHAR(50),           -- 'solution', 'pattern', 'error', 'optimization'
    category VARCHAR(50),
    tags TEXT[],
    
    -- Usage tracking
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    tokens INTEGER,
    
    metadata JSONB DEFAULT '{}'
);

-- Indexes for agent_knowledge
CREATE INDEX idx_agent_knowledge_hash ON agent_knowledge(content_hash);
CREATE INDEX idx_agent_knowledge_type ON agent_knowledge(knowledge_type);
CREATE INDEX idx_agent_knowledge_category ON agent_knowledge(category);
CREATE INDEX idx_agent_knowledge_created ON agent_knowledge(created_at DESC);
-- Vector similarity index (IVFFlat for performance)
CREATE INDEX idx_agent_knowledge_embedding ON agent_knowledge 
    USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);
-- Full-text search index
CREATE INDEX idx_agent_knowledge_content_fts ON agent_knowledge 
    USING GIN(to_tsvector('english', content));

-- ====================================================================
-- TABLE 4: agent_actions
-- Purpose: Comprehensive audit trail for all agent actions
-- ====================================================================
CREATE TABLE agent_actions (
    id SERIAL PRIMARY KEY,
    action_id VARCHAR(100) UNIQUE NOT NULL,
    session_id VARCHAR(100) REFERENCES agent_sessions(session_id),
    task_id VARCHAR(100) REFERENCES agent_tasks(task_id),
    
    -- Action details
    action_type VARCHAR(50) NOT NULL,     -- 'query', 'write', 'command', 'api_call', etc.
    action_description TEXT,
    
    -- Input/Output
    input_data JSONB,
    output_data JSONB,
    
    -- Execution
    executed_at TIMESTAMP DEFAULT NOW(),
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Audit
    changed_files TEXT[],
    commands_executed TEXT[],
    api_endpoints_called TEXT[],
    
    metadata JSONB DEFAULT '{}'
);

-- Indexes for agent_actions
CREATE INDEX idx_agent_actions_session ON agent_actions(session_id);
CREATE INDEX idx_agent_actions_task ON agent_actions(task_id);
CREATE INDEX idx_agent_actions_type ON agent_actions(action_type);
CREATE INDEX idx_agent_actions_executed ON agent_actions(executed_at DESC);
CREATE INDEX idx_agent_actions_success ON agent_actions(success);

-- ====================================================================
-- TABLE 5: agent_context_cache
-- Purpose: Landing context snapshots for performance optimization
-- ====================================================================
CREATE TABLE agent_context_cache (
    id SERIAL PRIMARY KEY,
    context_key VARCHAR(100) UNIQUE NOT NULL,
    context_version INTEGER DEFAULT 1,
    
    -- Context data
    system_state JSONB NOT NULL,
    documentation_index JSONB NOT NULL,
    active_services JSONB NOT NULL,
    current_tasks JSONB NOT NULL,
    performance_metrics JSONB NOT NULL,
    
    -- Metadata
    generated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    
    -- Size tracking
    context_size_bytes INTEGER,
    
    metadata JSONB DEFAULT '{}'
);

-- Indexes for agent_context_cache
CREATE INDEX idx_agent_context_key ON agent_context_cache(context_key);
CREATE INDEX idx_agent_context_expires ON agent_context_cache(expires_at);
CREATE INDEX idx_agent_context_generated ON agent_context_cache(generated_at DESC);

-- ====================================================================
-- SUMMARY
-- ====================================================================
-- Tables created: 5
-- Total indexes: 26
-- pgvector indexes: 1 (IVFFlat)
-- Full-text search indexes: 1 (GIN)
-- Foreign key constraints: 3
-- 
-- Prime Directives Compliance:
-- - All tables have actual data storage (NO theatrical wrappers)
-- - All indexes designed for real query performance
-- - Foreign keys ensure data integrity
-- - JSONB for flexible metadata without schema bloat
-- ====================================================================

-- Verification queries
SELECT 'Schema migration complete!' as status;
SELECT 'agent_sessions' as table_name, COUNT(*) as index_count FROM pg_indexes WHERE tablename = 'agent_sessions';
SELECT 'agent_tasks' as table_name, COUNT(*) as index_count FROM pg_indexes WHERE tablename = 'agent_tasks';
SELECT 'agent_knowledge' as table_name, COUNT(*) as index_count FROM pg_indexes WHERE tablename = 'agent_knowledge';
SELECT 'agent_actions' as table_name, COUNT(*) as index_count FROM pg_indexes WHERE tablename = 'agent_actions';
SELECT 'agent_context_cache' as table_name, COUNT(*) as index_count FROM pg_indexes WHERE tablename = 'agent_context_cache';

