#!/usr/bin/env python3
"""
Generate embeddings for LangChain documentation using standard embedding service
Uses BAAI/bge-base-en-v1.5 model (768 dimensions) via localhost:8765
Follows AYA embedding standards
"""

import psycopg2
import requests
import time
import json
import sys
from datetime import datetime

# Configuration
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
    """Sentence-boundary chunking to preserve semantic meaning"""
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
    """Generate single embedding via production service"""
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

def generate_embeddings_for_langchain():
    """Generate embeddings for LangChain documentation"""

    print(f"\n{'='*80}")
    print(f"EMBEDDING GENERATION: langchain_documentation")
    print(f"Project: aya")
    print(f"Model: {EMBEDDING_MODEL} (768 dimensions)")
    print(f"{'='*80}")

    # Test embedding service
    print("Testing embedding service...")
    test_embedding = get_embedding("test")
    if not test_embedding:
        print("❌ FAILED: Embedding service unavailable at", EMBEDDING_URL)
        print("Please start the embedding service:")
        print("  cd /Users/arthurdell/AYA/services")
        print("  nohup uvicorn embedding_service:app --host 0.0.0.0 --port 8765 > embedding.log 2>&1 &")
        return 0, 0, 0
    print(f"✅ Embedding service: {len(test_embedding)} dimensions")

    # Connect to database
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Database connected")

    # Get documents
    cursor.execute("""
        SELECT id, title, content
        FROM langchain_documentation
        ORDER BY id
    """)
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
                    'aya',
                    'langchain_documentation',
                    doc_id,
                    chunk_content,
                    chunk_idx,
                    embedding,
                    json.dumps({
                        'project': 'aya',
                        'table': 'langchain_documentation',
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

        if i % 10 == 0:
            conn.commit()
            elapsed = time.time() - start_overall
            rate = total_chunks / elapsed if elapsed > 0 else 0
            eta = (len(docs) - i) / (i / elapsed) if elapsed > 0 else 0
            print(f"  Progress: {i}/{len(docs)} docs ({i/len(docs)*100:.1f}%), {total_chunks} chunks, {rate:.1f} chunks/sec, ETA: {eta/60:.1f}min")

    conn.commit()

    elapsed_overall = time.time() - start_overall

    print(f"\n{'='*80}")
    print(f"COMPLETE: langchain_documentation")
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
    """Generate embeddings for LangChain documentation"""

    print("="*80)
    print("AYA EMBEDDING GENERATION - LANGCHAIN DOCUMENTATION")
    print(f"Started: {datetime.now()}")
    print("="*80)

    docs, chunks, elapsed = generate_embeddings_for_langchain()

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
