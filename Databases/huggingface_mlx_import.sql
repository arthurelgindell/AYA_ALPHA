-- https://huggingface.co/docs/hub/en/mlx Documentation Import
-- Generated: 2025-10-09T17:59:08.706849
-- Total documents: 2
-- Total words: 951
-- Source: https://huggingface.co/docs/hub/en/mlx

BEGIN;

DROP TABLE IF EXISTS mlx_documentation CASCADE;

CREATE TABLE mlx_documentation (
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

CREATE INDEX idx_mlx_documentation_url ON mlx_documentation(url);
CREATE INDEX idx_mlx_documentation_title ON mlx_documentation(title);
CREATE INDEX idx_mlx_documentation_section ON mlx_documentation(section_type);
CREATE INDEX idx_mlx_documentation_metadata ON mlx_documentation USING GIN(metadata);
CREATE INDEX idx_mlx_documentation_content_fts ON mlx_documentation USING GIN(to_tsvector('english', content));

COMMIT;
