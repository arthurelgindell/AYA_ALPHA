-- Intelligence Scout System - Database Schema
-- Creates queue and results tracking tables for automated technical intelligence gathering

BEGIN;

-- Queue for sites to crawl
CREATE TABLE IF NOT EXISTS intelligence_scout_queue (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    technology_name VARCHAR(100) NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    max_pages INTEGER DEFAULT 1000 CHECK (max_pages > 0),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'queued', 'crawling', 'processing', 'completed', 'failed', 'cancelled')),
    created_at TIMESTAMP DEFAULT NOW(),
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    pages_crawled INTEGER DEFAULT 0,
    crawl_id VARCHAR(255), -- Firecrawl crawl ID for tracking
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP
);

-- Results tracking
CREATE TABLE IF NOT EXISTS intelligence_scout_results (
    id SERIAL PRIMARY KEY,
    queue_id INTEGER REFERENCES intelligence_scout_queue(id) ON DELETE SET NULL,
    technology_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    pages_imported INTEGER DEFAULT 0,
    words_total INTEGER DEFAULT 0,
    embeddings_generated INTEGER DEFAULT 0,
    import_timestamp TIMESTAMP DEFAULT NOW(),
    knowledge_ids INTEGER[], -- References to agent_knowledge entries
    source_urls TEXT[], -- Array of crawled URLs
    metadata JSONB -- Additional metadata (version, categories, etc.)
);

-- Extend agent_knowledge for source tracking
ALTER TABLE agent_knowledge 
ADD COLUMN IF NOT EXISTS source_technology VARCHAR(100),
ADD COLUMN IF NOT EXISTS source_url TEXT,
ADD COLUMN IF NOT EXISTS scout_import_id INTEGER REFERENCES intelligence_scout_results(id);

-- Add indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_source_tech ON agent_knowledge(source_technology);
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_source_url ON agent_knowledge(source_url);
CREATE INDEX IF NOT EXISTS idx_scout_queue_status ON intelligence_scout_queue(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_scout_queue_technology ON intelligence_scout_queue(technology_name);
CREATE INDEX IF NOT EXISTS idx_scout_results_technology ON intelligence_scout_results(technology_name);
CREATE INDEX IF NOT EXISTS idx_scout_results_timestamp ON intelligence_scout_results(import_timestamp DESC);

COMMIT;

