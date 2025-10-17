# AYA EMBEDDING STANDARD - PRODUCTION SPECIFICATION
**Date**: October 10, 2025  
**Status**: MANDATORY FOR ALL PROJECTS  
**Scope**: aya_rag database and all future projects  
**Authority**: Production requirement for 100+ agentic AI agents

---

## EXECUTIVE SUMMARY

**MANDATORY STANDARD:**
- **Model**: BAAI/bge-base-en-v1.5
- **Endpoint**: http://localhost:8765/embed
- **Dimensions**: 768 (pgvector)
- **Performance**: 70 docs/second (validated)
- **Status**: Production operational ✅

**ALL content added to aya_rag MUST be embedded using this standard.**

---

## I. EMBEDDING SERVICE SPECIFICATION

### Service Configuration
```
Application: FastAPI/Uvicorn
Port: 8765
Model: BAAI/bge-base-en-v1.5
Framework: MLX (Metal-accelerated)
GPU: 80-core M3 Ultra
Process ID: 65125
Uptime: 14+ hours (stable)
Status: PRODUCTION OPERATIONAL ✅
```

### API Endpoints
```python
# Health Check
GET http://localhost:8765/health
Response: {"status": "healthy", "metal_available": true}

# Generate Embedding (Single)
POST http://localhost:8765/embed
Request: {"text": "your content here"}
Response: {"embedding": [768 floats]}

# Statistics
GET http://localhost:8765/stats
Response: {"embeddings_generated": N, "cache_size": M}
```

### Performance Characteristics
```
Single Embedding: 0.0543s - 0.1132s (average: ~0.08s)
Burst Load: 70.7 docs/second (sequential)
Large Documents: 3,250 chars in 0.0543s
Dimensions: 768
Metal Acceleration: Active
Stability: Validated 14+ hours uptime
```

---

## II. DATABASE SCHEMA STANDARD

### A. Content Tables (Project-Specific)

**MANDATORY columns for any table with text content:**

```sql
CREATE TABLE <project>_<table_name> (
    id SERIAL PRIMARY KEY,
    
    -- Content columns
    title TEXT,
    content TEXT NOT NULL,
    
    -- MANDATORY: Embedding tracking
    embedding_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'processing', 'complete', 'failed'
    embedding_model VARCHAR(100),                    -- 'bge-base-en-v1.5'
    embedding_generated_at TIMESTAMP,
    embedding_chunk_count INTEGER DEFAULT 0,
    
    -- MANDATORY: Metadata
    metadata JSONB DEFAULT '{}',
    
    -- MANDATORY: Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MANDATORY: Indexes
CREATE INDEX idx_<table>_embedding_status ON <table>(embedding_status);
CREATE INDEX idx_<table>_metadata ON <table> USING GIN(metadata);
CREATE INDEX idx_<table>_content_fts ON <table> USING GIN(to_tsvector('english', content));
```

### B. Unified Chunks Table (SHARED)

**MANDATORY structure for semantic search:**

```sql
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    
    -- Source tracking (MANDATORY)
    source_project VARCHAR(50),              -- 'aya', 'gladiator', 'project2'
    source_table VARCHAR(100),               -- Table name
    source_id INTEGER,                       -- ID in source table
    
    -- Legacy compatibility
    document_id INTEGER,                     -- NULL for documentation chunks
    
    -- Content (MANDATORY)
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0,
    
    -- Embedding (MANDATORY)
    embedding vector(768) NOT NULL,          -- pgvector 768-dimensional
    
    -- Metadata (MANDATORY)
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MANDATORY: Indexes for performance
CREATE INDEX idx_chunks_source ON chunks(source_project, source_table, source_id);
CREATE INDEX idx_chunks_document ON chunks(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX idx_chunks_metadata ON chunks USING GIN(metadata);
CREATE INDEX idx_chunks_embedding_cosine ON chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

**Current Status**: Partially implemented (missing source_project, source_table, source_id columns)

---

## III. EMBEDDING GENERATION STANDARD

### A. Reference Implementation

```python
#!/usr/bin/env python3
"""
AYA EMBEDDING GENERATION - PRODUCTION STANDARD
MANDATORY: Use this pattern for ALL tables
"""

import psycopg2
import requests
import time
from datetime import datetime

# STANDARD: Service configuration
EMBEDDING_URL = "http://localhost:8765/embed"
EMBEDDING_MODEL = "bge-base-en-v1.5"
CHUNK_SIZE = 1000  # characters
BATCH_DELAY = 0.015  # 15ms between requests (70 docs/sec)

# STANDARD: Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    """
    STANDARD: Sentence-boundary chunking
    
    Args:
        text: Full document text
        chunk_size: Target chunk size in characters
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Find sentence boundary
        if end < len(text):
            for i in range(end, max(start + chunk_size // 2, start), -1):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        start = end
    
    return chunks

def get_embedding(text: str) -> list:
    """
    STANDARD: Generate single embedding
    
    Args:
        text: Text to embed
    
    Returns:
        768-dimensional embedding vector
    """
    try:
        response = requests.post(
            EMBEDDING_URL,
            json={"text": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()['embedding']
    except Exception as e:
        print(f"ERROR generating embedding: {e}")
        return None

def generate_embeddings_for_table(
    table_name: str,
    project_name: str,
    title_column: str = 'title',
    content_column: str = 'content',
    where_clause: str = None
):
    """
    STANDARD: Generate embeddings for any table
    
    Args:
        table_name: Table to process (e.g., 'gladiator_documentation')
        project_name: Project identifier (e.g., 'gladiator')
        title_column: Name of title column
        content_column: Name of content column
        where_clause: Optional WHERE clause (e.g., "embedding_status = 'pending'")
    """
    
    print(f"\n{'='*80}")
    print(f"GENERATING EMBEDDINGS: {table_name}")
    print(f"Project: {project_name}")
    print(f"{'='*80}")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Build query
    query = f"""
        SELECT id, {title_column}, {content_column}
        FROM {table_name}
    """
    if where_clause:
        query += f" WHERE {where_clause}"
    
    cursor.execute(query)
    docs = cursor.fetchall()
    
    print(f"Documents to process: {len(docs)}")
    
    total_chunks = 0
    total_time = 0
    
    for i, (doc_id, title, content) in enumerate(docs, 1):
        # Combine title and content
        full_text = f"{title}\n\n{content}" if title else content
        if not full_text:
            continue
        
        # Create chunks
        chunks = chunk_text(full_text)
        
        # Generate embeddings for each chunk
        for chunk_idx, chunk_text in enumerate(chunks):
            start = time.time()
            embedding = get_embedding(chunk_text)
            duration = time.time() - start
            total_time += duration
            
            if embedding:
                # Insert into chunks table
                cursor.execute("""
                    INSERT INTO chunks (
                        chunk_text, embedding, chunk_index, metadata
                    ) VALUES (%s, %s, %s, %s)
                """, (
                    chunk_text,
                    embedding,
                    chunk_idx,
                    {
                        'table': table_name,
                        'doc_id': str(doc_id),
                        'chunk_idx': chunk_idx,
                        'title': title,
                        'project': project_name,
                        'embedding_model': EMBEDDING_MODEL,
                        'generated_at': datetime.now().isoformat()
                    }
                ))
                total_chunks += 1
                
                # Rate limiting
                time.sleep(BATCH_DELAY)
        
        # Update source table
        cursor.execute(f"""
            UPDATE {table_name}
            SET 
                embedding_status = 'complete',
                embedding_model = %s,
                embedding_generated_at = NOW(),
                embedding_chunk_count = %s
            WHERE id = %s
        """, (EMBEDDING_MODEL, len(chunks), doc_id))
        
        if i % 10 == 0:
            conn.commit()
            print(f"  Progress: {i}/{len(docs)} docs, {total_chunks} chunks, {total_chunks/total_time:.1f} chunks/sec")
    
    conn.commit()
    
    print(f"\n{'='*80}")
    print(f"COMPLETE: {table_name}")
    print(f"  Documents: {len(docs)}")
    print(f"  Chunks: {total_chunks}")
    print(f"  Time: {total_time:.2f}s")
    print(f"  Rate: {total_chunks/total_time:.1f} chunks/sec")
    print(f"{'='*80}")
    
    cursor.close()
    conn.close()
    
    return len(docs), total_chunks
```

### B. Usage Examples

**Example 1: New project table**
```python
# Generate embeddings for GLADIATOR documentation
generate_embeddings_for_table(
    table_name='gladiator_documentation',
    project_name='gladiator',
    title_column='title',
    content_column='content',
    where_clause="embedding_status = 'pending'"
)
```

**Example 2: Retroactive embedding**
```python
# Add embeddings to existing table
generate_embeddings_for_table(
    table_name='project2_notes',
    project_name='project2',
    title_column='note_title',
    content_column='note_body'
)
```

---

## IV. QUERY STANDARD

### A. Semantic Search (Universal)

```python
def semantic_search(
    query_text: str,
    project_filter: str = None,
    limit: int = 10,
    min_similarity: float = 0.5
) -> list:
    """
    STANDARD: Semantic search across all or filtered projects
    
    Args:
        query_text: Natural language query
        project_filter: Optional project name (e.g., 'gladiator')
        limit: Number of results
        min_similarity: Minimum cosine similarity (0-1)
    
    Returns:
        List of (chunk_text, similarity, source_project, source_table, source_id)
    """
    
    # Generate query embedding
    response = requests.post(
        "http://localhost:8765/embed",
        json={"text": query_text}
    )
    query_embedding = response.json()['embedding']
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    if project_filter:
        # Project-filtered search (FAST)
        cursor.execute("""
            SELECT 
                chunk_text,
                1 - (embedding <=> %s::vector) as similarity,
                metadata->>'project' as project,
                metadata->>'table' as source_table,
                (metadata->>'doc_id')::integer as doc_id,
                metadata->>'title' as title
            FROM chunks
            WHERE metadata->>'project' = %s
              AND 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, project_filter, query_embedding, min_similarity, query_embedding, limit))
    else:
        # Global search (ALL projects)
        cursor.execute("""
            SELECT 
                chunk_text,
                1 - (embedding <=> %s::vector) as similarity,
                metadata->>'project' as project,
                metadata->>'table' as source_table,
                (metadata->>'doc_id')::integer as doc_id,
                metadata->>'title' as title
            FROM chunks
            WHERE 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, min_similarity, query_embedding, limit))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results
```

### B. Hybrid Search (Full-Text + Vector)

```python
def hybrid_search(
    query_text: str,
    project_filter: str = None,
    limit: int = 10
) -> list:
    """
    STANDARD: Combine full-text and semantic search
    
    Returns results that match EITHER full-text OR semantic similarity
    """
    
    # Generate query embedding
    response = requests.post(
        "http://localhost:8765/embed",
        json={"text": query_text}
    )
    query_embedding = response.json()['embedding']
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Hybrid query
    cursor.execute("""
        WITH vector_results AS (
            SELECT 
                chunk_text,
                1 - (embedding <=> %s::vector) as similarity,
                metadata,
                'vector' as match_type
            FROM chunks
            WHERE metadata->>'project' = COALESCE(%s, metadata->>'project')
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        ),
        fts_results AS (
            SELECT 
                chunk_text,
                ts_rank(to_tsvector('english', chunk_text), to_tsquery('english', %s)) as similarity,
                metadata,
                'fulltext' as match_type
            FROM chunks
            WHERE to_tsvector('english', chunk_text) @@ to_tsquery('english', %s)
              AND metadata->>'project' = COALESCE(%s, metadata->>'project')
            LIMIT %s
        )
        SELECT * FROM vector_results
        UNION ALL
        SELECT * FROM fts_results
        ORDER BY similarity DESC
        LIMIT %s
    """, (
        query_embedding, project_filter, query_embedding, limit,
        query_text, query_text, project_filter, limit,
        limit
    ))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results
```

---

## III. OPERATIONAL PROCEDURES

### A. Adding New Project

**Step 1: Create project-specific tables**
```sql
-- Follow naming convention: <project>_<table>
CREATE TABLE myproject_documentation (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding_status VARCHAR(20) DEFAULT 'pending',
    embedding_model VARCHAR(100),
    embedding_generated_at TIMESTAMP,
    embedding_chunk_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Step 2: Populate with content**
```sql
INSERT INTO myproject_documentation (title, content, metadata)
VALUES ('Doc Title', 'Content here', '{"category": "architecture"}');
```

**Step 3: Generate embeddings**
```python
from embedding_standard import generate_embeddings_for_table

generate_embeddings_for_table(
    table_name='myproject_documentation',
    project_name='myproject'
)
```

**Step 4: Verify**
```sql
SELECT 
    COUNT(*) as docs,
    SUM(embedding_chunk_count) as chunks,
    COUNT(*) FILTER (WHERE embedding_status = 'complete') as embedded
FROM myproject_documentation;
```

### B. Query Patterns

**Pattern 1: Project-specific search**
```python
results = semantic_search(
    query_text="How to configure PostgreSQL?",
    project_filter="aya",
    limit=10
)
```

**Pattern 2: Cross-project search**
```python
results = semantic_search(
    query_text="Attack pattern SQL injection",
    project_filter=None,  # Search ALL projects
    limit=20
)
```

**Pattern 3: SQL direct query**
```sql
-- Search GLADIATOR project only
SELECT 
    chunk_text,
    metadata->>'title' as title,
    1 - (embedding <=> '[query_vector]'::vector) as similarity
FROM chunks
WHERE metadata->>'project' = 'gladiator'
ORDER BY embedding <=> '[query_vector]'::vector
LIMIT 10;
```

---

## IV. PERFORMANCE STANDARDS

### A. Service Level Objectives (SLO)

**Embedding Generation:**
- Single doc: <1 second (95th percentile)
- Burst load: >50 docs/second
- Uptime: >99.9% (excluding planned maintenance)
- Error rate: <0.1%

**Semantic Search:**
- Global search: <500ms (95th percentile)
- Project-filtered: <200ms (95th percentile)
- Concurrent agents (100): <1s per query
- Index performance: Must use IVFFlat index

### B. Scaling Guidelines

**Current Capacity:**
```
Hardware: Mac Studio M3 Ultra, 512GB RAM, 80-core GPU
Current load: 8,489 chunks embedded
Embedding service: 70 docs/sec sustained
Database: 231 MB, plenty of headroom

Projected capacity:
├─ GLADIATOR: 10M attack patterns → ~10M chunks
├─ Project 2-10: ~100K chunks each
└─ Total: ~11M chunks (estimated 8.5 GB vector data)

Performance impact:
├─ IVFFlat lists: Increase to 1000 (from 100) at 1M+ chunks
├─ Query latency: +100-200ms at 10M+ chunks
└─ Mitigation: Partition chunks table by project
```

**Scaling Triggers:**
- >1M chunks: Re-create IVFFlat index with lists=1000
- >10M chunks: Consider table partitioning
- >100 concurrent agents: Deploy PgBouncer connection pooling
- >1TB database: Move to dedicated PostgreSQL server

---

## V. MIGRATION STANDARD (Existing Tables)

### A. Enhance Chunks Table

```sql
-- Add standard columns to existing chunks table
ALTER TABLE chunks 
ADD COLUMN IF NOT EXISTS source_project VARCHAR(50),
ADD COLUMN IF NOT EXISTS source_table VARCHAR(100),
ADD COLUMN IF NOT EXISTS source_id INTEGER;

-- Backfill from metadata
UPDATE chunks 
SET 
    source_table = metadata->>'table',
    source_id = (metadata->>'doc_id')::integer,
    source_project = COALESCE(metadata->>'project', 'aya')  -- Default to 'aya'
WHERE metadata->>'table' IS NOT NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_chunks_source 
ON chunks(source_project, source_table, source_id);

CREATE INDEX IF NOT EXISTS idx_chunks_project 
ON chunks(source_project);
```

### B. Add Tracking Columns to Documentation Tables

```sql
-- Template for each existing documentation table
ALTER TABLE <table_name>
ADD COLUMN IF NOT EXISTS embedding_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100),
ADD COLUMN IF NOT EXISTS embedding_generated_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS embedding_chunk_count INTEGER DEFAULT 0;

-- Mark already-embedded docs as complete
UPDATE <table_name>
SET 
    embedding_status = 'complete',
    embedding_model = 'bge-base-en-v1.5',
    embedding_generated_at = '2025-10-10 05:25:13'
WHERE id IN (
    SELECT DISTINCT (metadata->>'doc_id')::integer
    FROM chunks
    WHERE metadata->>'table' = '<table_name>'
);
```

---

## VI. MONITORING & MAINTENANCE

### A. Health Checks

```bash
# Embedding service health
curl http://localhost:8765/health

# Expected: {"status": "healthy", "metal_available": true}
```

```sql
-- Chunks table health
SELECT 
    COUNT(*) as total_chunks,
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) as with_embedding,
    pg_size_pretty(pg_total_relation_size('chunks')) as size,
    COUNT(DISTINCT metadata->>'project') as projects
FROM chunks;
```

### B. Performance Monitoring

```sql
-- Embedding coverage per project
SELECT 
    metadata->>'project' as project,
    metadata->>'table' as source_table,
    COUNT(*) as chunks,
    pg_size_pretty(SUM(octet_length(embedding::text)::bigint)) as embedding_size
FROM chunks
GROUP BY metadata->>'project', metadata->>'table'
ORDER BY project, source_table;
```

### C. Query Performance

```sql
-- Check index usage
EXPLAIN ANALYZE
SELECT chunk_text, 1 - (embedding <=> '[query_vector]'::vector) as similarity
FROM chunks
WHERE metadata->>'project' = 'gladiator'
ORDER BY embedding <=> '[query_vector]'::vector
LIMIT 10;

-- Should show: Index Scan using idx_chunks_embedding_cosine
```

---

## VII. TROUBLESHOOTING

### Issue: Embedding service unavailable
```bash
# Check process
ps aux | grep embedding_service

# Restart if needed
cd /Users/arthurdell/AYA/services
python3 embedding_service.py &

# Verify
curl http://localhost:8765/health
```

### Issue: Slow query performance
```sql
-- Check if index is being used
EXPLAIN SELECT ... ORDER BY embedding <=> ...;

-- If not using IVFFlat index, recreate:
DROP INDEX idx_chunks_embedding_cosine;
CREATE INDEX idx_chunks_embedding_cosine ON chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Analyze table
ANALYZE chunks;
```

### Issue: Memory exhaustion
```bash
# Check embedding service RAM usage
ps aux | grep embedding_service | awk '{print $6/1024 " MB"}'

# If >50GB, restart service
```

---

## VIII. COMPLIANCE CHECKLIST

**For ANY new table added to aya_rag:**

- [ ] Table has title/content columns
- [ ] Added embedding_status, embedding_model, embedding_generated_at columns
- [ ] Created full-text search index (GIN)
- [ ] Created metadata index (GIN)
- [ ] Generated embeddings using standard script
- [ ] Verified chunks inserted into chunks table
- [ ] Tested semantic search on content
- [ ] Documented in project README

**If ANY checkbox unchecked, table is NOT compliant.**

---

## IX. CURRENT PRODUCTION STATE

**Embedding Coverage (as of Oct 10, 2025):**
```
postgresql_documentation: ✅ 1,143 chunks
docker_documentation:     ✅ 3,007 chunks
zapier_documentation:     ✅ 2,005 chunks
crush_documentation:      ✅ 2,027 chunks
firecrawl_docs:          ✅ 267 chunks
lmstudio_documentation:  ✅ 37 chunks
mlx_documentation:       ✅ 2 chunks
documents (Prime Directives): ✅ 1 chunk

TOTAL: 8,489 chunks with 768D embeddings
Model: BAAI/bge-base-en-v1.5
Status: PRODUCTION OPERATIONAL
```

**Next Projects:**
- GLADIATOR: Pending deployment
- Future projects: Follow this standard

---

## X. REFERENCE IMPLEMENTATION

**Location**: `/Users/arthurdell/AYA/services/generate_embeddings_standard.py`

**This script is the SINGLE SOURCE OF TRUTH for embedding generation.**

---

**END OF EMBEDDING STANDARD**

**Status**: MANDATORY FOR ALL AYA PROJECTS  
**Compliance**: 100% required  
**Exceptions**: NONE

**Questions**: Contact infrastructure team

