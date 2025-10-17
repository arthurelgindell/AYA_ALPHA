-- https://www.postgresql.org/docs/18/ Documentation Import
-- Generated: 2025-10-09T17:18:01.900827
-- Total documents: 1143
-- Total words: 1,481,081
-- Source: https://www.postgresql.org/docs/18/

BEGIN;

DROP TABLE IF EXISTS postgresql_documentation CASCADE;

CREATE TABLE postgresql_documentation (
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

CREATE INDEX idx_postgresql_documentation_url ON postgresql_documentation(url);
CREATE INDEX idx_postgresql_documentation_title ON postgresql_documentation(title);
CREATE INDEX idx_postgresql_documentation_section ON postgresql_documentation(section_type);
CREATE INDEX idx_postgresql_documentation_metadata ON postgresql_documentation USING GIN(metadata);
CREATE INDEX idx_postgresql_documentation_content_fts ON postgresql_documentation USING GIN(to_tsvector('english', content));

COMMIT;
