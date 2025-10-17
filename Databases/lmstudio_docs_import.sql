-- https://lmstudio.ai/docs/app Documentation Import
-- Generated: 2025-10-09T17:14:21.155273
-- Total documents: 37
-- Total words: 20,042
-- Source: https://lmstudio.ai/docs/app

BEGIN;

DROP TABLE IF EXISTS lmstudio_documentation CASCADE;

CREATE TABLE lmstudio_documentation (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    description TEXT,
    content TEXT,
    markdown TEXT,
    metadata JSONB,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER,
    section_type TEXT
);

CREATE INDEX idx_lmstudio_documentation_url ON lmstudio_documentation(url);
CREATE INDEX idx_lmstudio_documentation_title ON lmstudio_documentation(title);
CREATE INDEX idx_lmstudio_documentation_section ON lmstudio_documentation(section_type);
CREATE INDEX idx_lmstudio_documentation_metadata ON lmstudio_documentation USING GIN(metadata);
CREATE INDEX idx_lmstudio_documentation_content_fts ON lmstudio_documentation USING GIN(to_tsvector('english', content));

COMMIT;
