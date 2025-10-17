#!/usr/bin/env python3
"""
AYA EMBEDDING GENERATION - PRODUCTION STANDARD
MANDATORY: Use this for ALL table embedding generation

Service: http://localhost:8765/embed
Model: BAAI/bge-base-en-v1.5
Dimensions: 768
Performance: 70 docs/second
"""

import psycopg2
import requests
import time
import json
import sys
from datetime import datetime

# STANDARD: Configuration
EMBEDDING_URL = "http://localhost:8765/embed"
EMBEDDING_MODEL = "bge-base-en-v1.5"
CHUNK_SIZE = 1000  # characters
RATE_LIMIT_DELAY = 0.015  # 15ms between requests (70 docs/sec max)

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
    Splits text at sentence boundaries to preserve semantic meaning
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
        if chunk:
            chunks.append(chunk)
        start = end
    
    return chunks

def get_embedding(text: str) -> list:
    """
    STANDARD: Generate single embedding via production service
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
        print(f"  ⚠️  ERROR: {e}")
        return None

def generate_embeddings_for_table(
    table_name: str,
    project_name: str,
    title_column: str = 'title',
    content_column: str = 'content',
    where_clause: str = None,
    dry_run: bool = False
):
    """
    STANDARD: Generate embeddings for any table
    
    Args:
        table_name: Table to process (e.g., 'gladiator_documentation')
        project_name: Project identifier (e.g., 'gladiator')
        title_column: Name of title column
        content_column: Name of content column
        where_clause: Optional WHERE clause
        dry_run: If True, don't insert to database
    
    Returns:
        (docs_processed, chunks_created, time_elapsed)
    """
    
    print(f"\n{'='*80}")
    print(f"EMBEDDING GENERATION: {table_name}")
    print(f"Project: {project_name}")
    print(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
    print(f"{'='*80}")
    
    # Test embedding service
    test_embedding = get_embedding("test")
    if not test_embedding:
        print("❌ FAILED: Embedding service unavailable at", EMBEDDING_URL)
        return 0, 0, 0
    print(f"✅ Embedding service: {len(test_embedding)} dimensions")
    
    # Connect to database
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
    
    if len(docs) == 0:
        print("⚠️  No documents to process")
        cursor.close()
        conn.close()
        return 0, 0, 0
    
    total_chunks = 0
    total_time = 0
    start_overall = time.time()
    
    for i, (doc_id, title, content) in enumerate(docs, 1):
        # Combine title and content
        full_text = ""
        if title:
            full_text += title
        if title and content:
            full_text += "\n\n"
        if content:
            full_text += content
        
        if not full_text:
            continue
        
        # Create chunks
        doc_chunks = chunk_text(full_text)
        
        # Generate embeddings for each chunk
        for chunk_idx, chunk_content in enumerate(doc_chunks):
            start = time.time()
            embedding = get_embedding(chunk_content)
            duration = time.time() - start
            total_time += duration
            
            if embedding:
                if not dry_run:
                    # Insert into chunks table with standard metadata
                    cursor.execute("""
                        INSERT INTO chunks (
                            source_project,
                            source_table,
                            source_id,
                            chunk_text,
                            chunk_index,
                            embedding,
                            metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        project_name,
                        table_name,
                        doc_id,
                        chunk_content,
                        chunk_idx,
                        embedding,
                        json.dumps({
                            'project': project_name,
                            'table': table_name,
                            'doc_id': str(doc_id),
                            'chunk_idx': chunk_idx,
                            'title': title,
                            'embedding_model': EMBEDDING_MODEL,
                            'generated_at': datetime.now().isoformat()
                        })
                    ))
                
                total_chunks += 1
                
                # Rate limiting
                time.sleep(RATE_LIMIT_DELAY)
        
        # Update source table
        if not dry_run:
            cursor.execute(f"""
                UPDATE {table_name}
                SET 
                    embedding_status = 'complete',
                    embedding_model = %s,
                    embedding_generated_at = NOW(),
                    embedding_chunk_count = %s
                WHERE id = %s
            """, (EMBEDDING_MODEL, len(doc_chunks), doc_id))
        
        if i % 10 == 0:
            if not dry_run:
                conn.commit()
            elapsed = time.time() - start_overall
            rate = total_chunks / elapsed if elapsed > 0 else 0
            eta = (len(docs) - i) / (i / elapsed) if elapsed > 0 else 0
            print(f"  Progress: {i}/{len(docs)} docs ({i/len(docs)*100:.1f}%), {total_chunks} chunks, {rate:.1f} chunks/sec, ETA: {eta/60:.1f}min")
    
    if not dry_run:
        conn.commit()
    
    elapsed_overall = time.time() - start_overall
    
    print(f"\n{'='*80}")
    print(f"COMPLETE: {table_name}")
    print(f"  Documents: {len(docs)}")
    print(f"  Chunks: {total_chunks}")
    print(f"  Time: {elapsed_overall:.2f}s ({elapsed_overall/60:.1f} minutes)")
    print(f"  Rate: {total_chunks/elapsed_overall:.1f} chunks/sec")
    print(f"  Avg per doc: {elapsed_overall/len(docs):.2f}s")
    print(f"{'='*80}")
    
    cursor.close()
    conn.close()
    
    return len(docs), total_chunks, elapsed_overall

def main():
    """Generate embeddings for specified table or all GLADIATOR tables"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 generate_embeddings_standard.py <table_name> <project_name> [--dry-run]")
        print("\nExamples:")
        print("  python3 generate_embeddings_standard.py gladiator_documentation gladiator")
        print("  python3 generate_embeddings_standard.py myproject_notes myproject --dry-run")
        sys.exit(1)
    
    table_name = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else 'aya'
    dry_run = '--dry-run' in sys.argv
    
    print("="*80)
    print("AYA EMBEDDING GENERATION - PRODUCTION STANDARD")
    print(f"Started: {datetime.now()}")
    print(f"Table: {table_name}")
    print(f"Project: {project_name}")
    print("="*80)
    
    docs, chunks, elapsed = generate_embeddings_for_table(
        table_name=table_name,
        project_name=project_name,
        dry_run=dry_run
    )
    
    print("\n" + "="*80)
    print("EMBEDDING GENERATION COMPLETE")
    print(f"Completed: {datetime.now()}")
    print(f"Total documents: {docs}")
    print(f"Total chunks: {chunks}")
    print(f"Total time: {elapsed:.2f}s ({elapsed/60:.1f} minutes)")
    if chunks > 0:
        print(f"Average rate: {chunks/elapsed:.1f} embeddings/second")
    print("="*80)

if __name__ == "__main__":
    main()

