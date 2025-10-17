-- https://www.docker.com Documentation Import
-- Generated: 2025-10-09T17:27:32.682870
-- Total documents: 2000
-- Total words: 1,936,078
-- Source: https://www.docker.com

BEGIN;

DROP TABLE IF EXISTS docker_documentation CASCADE;

CREATE TABLE docker_documentation (
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

CREATE INDEX idx_docker_documentation_url ON docker_documentation(url);
CREATE INDEX idx_docker_documentation_title ON docker_documentation(title);
CREATE INDEX idx_docker_documentation_section ON docker_documentation(section_type);
CREATE INDEX idx_docker_documentation_metadata ON docker_documentation USING GIN(metadata);
CREATE INDEX idx_docker_documentation_content_fts ON docker_documentation USING GIN(to_tsvector('english', content));

COMMIT;
