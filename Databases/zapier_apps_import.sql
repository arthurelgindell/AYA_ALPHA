-- https://zapier.com/apps Documentation Import
-- Generated: 2025-10-09T18:00:12.227074
-- Total documents: 2005
-- Total words: 5,786,237
-- Source: https://zapier.com/apps

BEGIN;

DROP TABLE IF EXISTS zapier_documentation CASCADE;

CREATE TABLE zapier_documentation (
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

CREATE INDEX idx_zapier_documentation_url ON zapier_documentation(url);
CREATE INDEX idx_zapier_documentation_title ON zapier_documentation(title);
CREATE INDEX idx_zapier_documentation_section ON zapier_documentation(section_type);
CREATE INDEX idx_zapier_documentation_metadata ON zapier_documentation USING GIN(metadata);
CREATE INDEX idx_zapier_documentation_content_fts ON zapier_documentation USING GIN(to_tsvector('english', content));

COMMIT;
