#!/usr/bin/env python3
"""
Generate embeddings for AYA documentation using LM Studio
Uses batch processing for maximum efficiency
"""

import psycopg2
import requests
import json
import time
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

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

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

def process_table(table_name, conn, limit=None):
    """Process a documentation table and generate embeddings"""
    print(f"\n{'='*60}")
    print(f"Processing table: {table_name}")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM {table_name}"
    if limit:
        count_query += f" LIMIT {limit}"
    cursor.execute(count_query)
    total_docs = cursor.fetchone()[0]
    print(f"Total documents: {total_docs}")
    
    # Fetch documents
    query = f"SELECT id, title, content FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    
    docs = cursor.fetchall()
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
        chunks = chunk_text(text_to_chunk)
        
        for chunk_idx, chunk_text in enumerate(chunks):
            batch_texts.append(chunk_text)
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
                    # Insert into chunks table
                    insert_chunks(cursor, batch_metadata, batch_texts, embeddings)
                    total_embeddings += len(embeddings)
                    print(f"  Progress: {i}/{len(docs)} docs, {total_embeddings} embeddings generated")
                
                batch_texts = []
                batch_metadata = []
        
        if i % 10 == 0:
            conn.commit()
    
    # Process remaining batch
    if batch_texts:
        embeddings = get_embeddings_batch(batch_texts)
        if embeddings:
            insert_chunks(cursor, batch_metadata, batch_texts, embeddings)
            total_embeddings += len(embeddings)
    
    conn.commit()
    
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Table {table_name} complete:")
    print(f"  Documents processed: {len(docs)}")
    print(f"  Chunks created: {total_chunks}")
    print(f"  Embeddings generated: {total_embeddings}")
    print(f"  Time elapsed: {elapsed:.2f}s")
    print(f"  Rate: {total_embeddings/elapsed:.2f} embeddings/second")
    print(f"{'='*60}")
    
    cursor.close()
    return total_chunks, total_embeddings

def insert_chunks(cursor, metadata_list, texts, embeddings):
    """Insert chunks with embeddings into database"""
    # Note: We're inserting into the existing chunks table
    # This assumes chunks table is for general purpose, not just documents table
    # May need to create separate table or modify schema
    
    for meta, text, embedding in zip(metadata_list, texts, embeddings):
        # For now, insert with document_id = NULL and store metadata in chunk_text
        # TODO: Modify schema to support documentation chunks properly
        chunk_text = f"[{meta['table']}:{meta['doc_id']}] {meta['title']}\n\n{text}"
        
        cursor.execute("""
            INSERT INTO chunks (document_id, chunk_text, embedding, chunk_index, metadata)
            VALUES (NULL, %s, %s, %s, %s)
        """, (
            chunk_text,
            embedding,
            meta['chunk_idx'],
            json.dumps(meta)
        ))

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
    
    # Connect to database
    print("\nConnecting to PostgreSQL...")
    conn = connect_db()
    print("✅ Database connected")
    
    # Process each table
    total_chunks = 0
    total_embeddings = 0
    
    for table in DOC_TABLES:
        chunks, embeddings = process_table(table, conn)
        total_chunks += chunks
        total_embeddings += embeddings
    
    conn.close()
    
    print("\n" + "="*60)
    print("EMBEDDING GENERATION COMPLETE")
    print(f"Completed: {datetime.now()}")
    print("="*60)
    print(f"Total chunks created: {total_chunks}")
    print(f"Total embeddings generated: {total_embeddings}")
    print("="*60)

if __name__ == "__main__":
    main()
