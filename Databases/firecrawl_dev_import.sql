-- https://www.firecrawl.dev Documentation Import
-- Generated: 2025-10-09T17:12:09.404098
-- Total documents: 254
-- Total words: 687,547
-- Source: https://www.firecrawl.dev

BEGIN;

DROP TABLE IF EXISTS firecrawl_docs CASCADE;

CREATE TABLE firecrawl_docs (
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

CREATE INDEX idx_firecrawl_docs_url ON firecrawl_docs(url);
CREATE INDEX idx_firecrawl_docs_title ON firecrawl_docs(title);
CREATE INDEX idx_firecrawl_docs_section ON firecrawl_docs(section_type);
CREATE INDEX idx_firecrawl_docs_metadata ON firecrawl_docs USING GIN(metadata);
CREATE INDEX idx_firecrawl_docs_content_fts ON firecrawl_docs USING GIN(to_tsvector('english', content));

COMMIT;
