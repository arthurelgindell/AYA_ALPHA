#!/usr/bin/env python3
"""
Generate embeddings for AYA documentation using LM Studio
Uses PostgreSQL CLI tools (psql) to avoid psycopg2 import issues
Uses batch processing for maximum efficiency
"""

import requests
import json
import time
import subprocess
from datetime import datetime

# Configuration
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "aya_rag"
DB_USER = "postgres"
DB_PASSWORD = "Power$$336633$$"

LMSTUDIO_URL = "http://localhost:1234/v1/embeddings"
LMSTUDIO_MODEL = "text-embedding-nomic-embed-text-v1.5"
BATCH_SIZE = 100
CHUNK_SIZE = 1000  # Characters per chunk

# Documentation tables to process
DOC_TABLES = [
    'postgresql_documentation',
    'docker_documentation',
    'zapier_documentation',
    'crush_documentation',
    'firecrawl_docs',
    'lmstudio_documentation',
    'mlx_documentation'
]

def run_psql(query):
    """Execute PostgreSQL query using psql CLI"""
    env = {"PGPASSWORD": DB_PASSWORD}
    cmd = [
        "/Library/PostgreSQL/18/bin/psql",
        "-U", DB_USER,
        "-d", DB_NAME,
        "-t",  # Tuples only
        "-A",  # Unaligned output
        "-F", "\t",  # Tab separator
        "-c", query
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return None
    return result.stdout.strip()

def run_psql_copy(query, data):
    """Execute PostgreSQL COPY command with data"""
    env = {"PGPASSWORD": DB_PASSWORD}
    cmd = [
        "/Library/PostgreSQL/18/bin/psql",
        "-U", DB_USER,
        "-d", DB_NAME,
        "-c", query
    ]

    result = subprocess.run(cmd, input=data, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    return True

def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into chunks of approximately chunk_size characters"""
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end
            for i in range(end, max(start + chunk_size // 2, start), -1):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        chunks.append(text[start:end].strip())
        start = end
    return chunks

def get_embeddings_batch(texts):
    """Get embeddings for a batch of texts from LM Studio"""
    try:
        response = requests.post(
            LMSTUDIO_URL,
            json={"input": texts, "model": LMSTUDIO_MODEL},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return [item['embedding'] for item in data['data']]
    except Exception as e:
        print(f"ERROR getting embeddings: {e}")
        return None

def insert_chunk(doc_id, table_name, chunk_idx, chunk_text, embedding, title):
    """Insert a single chunk with embedding into database"""
    # Format chunk text with metadata
    full_chunk_text = f"[{table_name}:{doc_id}] {title}\n\n{chunk_text}"

    # Escape single quotes in text
    escaped_text = full_chunk_text.replace("'", "''")

    # Format embedding as PostgreSQL array
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    # Create metadata JSON
    metadata = {
        'table': table_name,
        'doc_id': doc_id,
        'title': title,
        'chunk_idx': chunk_idx
    }
    metadata_json = json.dumps(metadata).replace("'", "''")

    # Insert query
    query = f"""
    INSERT INTO chunks (document_id, chunk_text, embedding, chunk_index, metadata)
    VALUES (NULL, '{escaped_text}', '{embedding_str}', {chunk_idx}, '{metadata_json}');
    """

    result = run_psql(query)
    return result is not None

def process_table(table_name, limit=None):
    """Process a documentation table and generate embeddings"""
    print(f"\n{'='*60}")
    print(f"Processing table: {table_name}")
    print(f"{'='*60}")

    # Get total count
    count_query = f"SELECT COUNT(*) FROM {table_name}"
    if limit:
        count_query += f" LIMIT {limit}"

    total_docs = run_psql(count_query)
    if not total_docs:
        print("ERROR: Could not get document count")
        return 0, 0

    print(f"Total documents: {total_docs}")

    # Fetch documents
    query = f"SELECT id, title, content FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"

    result = run_psql(query)
    if not result:
        print("ERROR: Could not fetch documents")
        return 0, 0

    # Parse results
    docs = []
    for line in result.split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            doc_id = parts[0]
            title = parts[1] if parts[1] else ""
            content = parts[2] if parts[2] else ""
            docs.append((doc_id, title, content))

    print(f"Fetched {len(docs)} documents")

    # Process in batches
    total_chunks = 0
    total_embeddings = 0
    batch_texts = []
    batch_metadata = []

    start_time = time.time()

    for i, (doc_id, title, content) in enumerate(docs, 1):
        # Create chunks
        text_to_chunk = f"{title}\n\n{content}" if title and content else (title or content or "")
        text_chunks = chunk_text(text_to_chunk)

        for chunk_idx, chunk_content in enumerate(text_chunks):
            batch_texts.append(chunk_content)
            batch_metadata.append({
                'table': table_name,
                'doc_id': doc_id,
                'chunk_idx': chunk_idx,
                'title': title
            })
            total_chunks += 1

            # Process batch when full
            if len(batch_texts) >= BATCH_SIZE:
                embeddings = get_embeddings_batch(batch_texts)
                if embeddings:
                    # Insert chunks one by one
                    for meta, text, embedding in zip(batch_metadata, batch_texts, embeddings):
                        insert_chunk(
                            meta['doc_id'],
                            meta['table'],
                            meta['chunk_idx'],
                            text,
                            embedding,
                            meta['title']
                        )
                    total_embeddings += len(embeddings)
                    print(f"  Progress: {i}/{len(docs)} docs, {total_embeddings} embeddings generated")

                batch_texts = []
                batch_metadata = []

    # Process remaining batch
    if batch_texts:
        embeddings = get_embeddings_batch(batch_texts)
        if embeddings:
            for meta, text, embedding in zip(batch_metadata, batch_texts, embeddings):
                insert_chunk(
                    meta['doc_id'],
                    meta['table'],
                    meta['chunk_idx'],
                    text,
                    embedding,
                    meta['title']
                )
            total_embeddings += len(embeddings)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Table {table_name} complete:")
    print(f"  Documents processed: {len(docs)}")
    print(f"  Chunks created: {total_chunks}")
    print(f"  Embeddings generated: {total_embeddings}")
    print(f"  Time elapsed: {elapsed:.2f}s")
    print(f"  Rate: {total_embeddings/elapsed:.2f} embeddings/second")
    print(f"{'='*60}")

    return total_chunks, total_embeddings

def main():
    print("="*60)
    print("AYA EMBEDDING GENERATION - LM Studio")
    print(f"Started: {datetime.now()}")
    print("="*60)

    # Test LM Studio connection
    print("\nTesting LM Studio connection...")
    test_embedding = get_embeddings_batch(["test"])
    if not test_embedding:
        print("ERROR: Cannot connect to LM Studio at localhost:1234")
        print("Please ensure LM Studio is running with embedding model loaded")
        return
    print(f"✅ LM Studio connected (embedding dimension: {len(test_embedding[0])})")

    # Test database connection
    print("\nTesting database connection...")
    version = run_psql("SELECT version();")
    if not version:
        print("ERROR: Cannot connect to PostgreSQL")
        return
    print("✅ Database connected")

    # Process each table
    total_chunks = 0
    total_embeddings = 0

    for table in DOC_TABLES:
        chunks, embeddings = process_table(table)
        total_chunks += chunks
        total_embeddings += embeddings

    print("\n" + "="*60)
    print("EMBEDDING GENERATION COMPLETE")
    print(f"Completed: {datetime.now()}")
    print("="*60)
    print(f"Total chunks created: {total_chunks}")
    print(f"Total embeddings generated: {total_embeddings}")
    print("="*60)

if __name__ == "__main__":
    main()
