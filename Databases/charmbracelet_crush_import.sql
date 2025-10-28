-- https://github.com/charmbracelet/crush Documentation Import
-- Generated: 2025-10-09T17:39:58.256111
-- Total documents: 2000
-- Total words: 1,318,164
-- Source: https://github.com/charmbracelet/crush

BEGIN;

DROP TABLE IF EXISTS crush_documentation CASCADE;

CREATE TABLE crush_documentation (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) NOT NULL UNIQUE,      -- URL length limit for index efficiency
    title VARCHAR(512) NOT NULL,            -- Required title field
    description TEXT,
    content TEXT NOT NULL,                  -- Core documentation required
    markdown TEXT,
    metadata JSONB,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER CHECK (word_count >= 0),  -- Non-negative constraint
    section_type VARCHAR(50)                -- Section categorization
);

CREATE INDEX idx_crush_documentation_url ON crush_documentation(url);
CREATE INDEX idx_crush_documentation_title ON crush_documentation(title);
CREATE INDEX idx_crush_documentation_section ON crush_documentation(section_type);
CREATE INDEX idx_crush_documentation_metadata ON crush_documentation USING GIN(metadata);
CREATE INDEX idx_crush_documentation_content_fts ON crush_documentation USING GIN(to_tsvector('english', content));

COMMIT;
