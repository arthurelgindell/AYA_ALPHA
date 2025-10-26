-- HuggingFace MLX Documentation Import
-- Generated: 2025-10-09T17:59:08.706849
-- Total documents: 2
-- Total words: 951
-- Source: https://huggingface.co/docs/hub/en/mlx
--
-- Table Purpose: Stores MLX (Apple Silicon machine learning) documentation from HuggingFace
-- Used for: AI model knowledge base, RAG queries, developer reference
-- Update Frequency: Weekly (documentation changes)

BEGIN;

DROP TABLE IF EXISTS mlx_documentation CASCADE;

CREATE TABLE mlx_documentation (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,                    -- Required field for searchability
    description TEXT,
    content TEXT NOT NULL,                  -- Required - core documentation content
    markdown TEXT NOT NULL,                 -- Required - original format preserved
    metadata JSONB,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER CHECK (word_count >= 0),  -- Ensure non-negative
    section_type TEXT
);

-- Index comments for clarity
COMMENT ON INDEX idx_mlx_documentation_url IS 'Optimizes URL lookups and deduplication';
COMMENT ON INDEX idx_mlx_documentation_title IS 'Supports title-based searches';
COMMENT ON INDEX idx_mlx_documentation_section IS 'Enables section filtering';
COMMENT ON INDEX idx_mlx_documentation_metadata IS 'GIN index for JSONB queries on metadata fields';
COMMENT ON INDEX idx_mlx_documentation_content_fts IS 'Full-text search on documentation content';

CREATE INDEX idx_mlx_documentation_url ON mlx_documentation(url);
CREATE INDEX idx_mlx_documentation_title ON mlx_documentation(title);
CREATE INDEX idx_mlx_documentation_section ON mlx_documentation(section_type);
CREATE INDEX idx_mlx_documentation_metadata ON mlx_documentation USING GIN(metadata);
CREATE INDEX idx_mlx_documentation_content_fts ON mlx_documentation USING GIN(to_tsvector('english', content));

COMMIT;
