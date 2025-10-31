#!/usr/bin/env python3
"""
Generate Embeddings for Gladiator Attack Patterns
Uses the existing embedding service at localhost:8765 to generate vector embeddings

Created: October 29, 2025
"""

import json
import psycopg2
import requests
import time
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

# Embedding service (MLX-powered service on port 8765)
EMBEDDING_SERVICE_URL = "http://localhost:8765"

def get_embedding(text: str) -> list:
    """Get embedding from the existing MLX embedding service"""
    try:
        response = requests.post(
            f"{EMBEDDING_SERVICE_URL}/embed",
            json={"text": text},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        # Service returns embedding directly
        return data['embedding']
    except Exception as e:
        print(f"  ⚠️  Embedding error: {e}")
        return None

def generate_embeddings(batch_size=50):
    """Generate embeddings for all Gladiator attack patterns"""
    
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  GLADIATOR EMBEDDING GENERATOR                        ║")
    print("║  Using MLX Embedding Service (localhost:8765)         ║")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check embedding service
    try:
        health = requests.get(f"{EMBEDDING_SERVICE_URL}/health", timeout=5).json()
        print(f"✅ Embedding service: {health}")
        print(f"   Metal available: {health.get('metal_available', False)}")
        print(f"   Model loaded: {health.get('model_loaded', False)}")
    except Exception as e:
        print(f"❌ Embedding service unavailable: {e}")
        print(f"   Make sure the embedding service is running on port 8765")
        cursor.close()
        conn.close()
        return
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM gladiator_attack_patterns WHERE embedding IS NULL")
    total_without_embeddings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM gladiator_attack_patterns")
    total_patterns = cursor.fetchone()[0]
    
    print(f"\n📊 Statistics:")
    print(f"   Total patterns: {total_patterns}")
    print(f"   Without embeddings: {total_without_embeddings}")
    print(f"   Batch size: {batch_size}")
    print(f"\n{'='*60}\n")
    
    if total_without_embeddings == 0:
        print("✅ All patterns already have embeddings!")
        cursor.close()
        conn.close()
        return
    
    # Fetch patterns without embeddings
    cursor.execute("""
        SELECT id, pattern_id, attack_type, description, payload
        FROM gladiator_attack_patterns
        WHERE embedding IS NULL
        ORDER BY id
    """)
    
    patterns = cursor.fetchall()
    total = len(patterns)
    print(f"Processing {total} patterns...\n")
    
    processed = 0
    errors = 0
    start_time = time.time()
    
    for idx, (id, pattern_id, attack_type, description, payload) in enumerate(patterns, 1):
        try:
            # Create embedding text from description and attack_type
            # Limit payload to first 500 chars to avoid overwhelming the model
            embedding_text = f"{attack_type}: {description or ''}"
            if payload:
                embedding_text += f" {payload[:500]}"
            
            # Truncate to reasonable length (most embedding models have limits)
            embedding_text = embedding_text[:2000]
            
            # Get embedding
            embedding = get_embedding(embedding_text)
            
            if embedding:
                # Update database
                cursor.execute("""
                    UPDATE gladiator_attack_patterns
                    SET embedding = %s
                    WHERE id = %s
                """, (embedding, id))
                
                processed += 1
                
                # Commit in batches
                if processed % batch_size == 0:
                    conn.commit()
                    elapsed = time.time() - start_time
                    rate = processed / elapsed if elapsed > 0 else 0
                    eta = (total - processed) / rate if rate > 0 else 0
                    print(f"  Progress: {processed}/{total} ({processed*100/total:.1f}%) | "
                          f"Rate: {rate:.1f}/s | ETA: {eta/60:.1f} min")
            else:
                errors += 1
                
        except Exception as e:
            errors += 1
            if errors % 10 == 0:
                print(f"  ⚠️  {errors} errors so far (continuing...)")
            continue
    
    # Final commit
    conn.commit()
    cursor.close()
    conn.close()
    
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"\n✅ EMBEDDING GENERATION COMPLETE")
    print(f"\n📊 Final Statistics:")
    print(f"   Processed: {processed}")
    print(f"   Errors: {errors}")
    print(f"   Time: {elapsed/60:.2f} minutes")
    print(f"   Average rate: {processed/elapsed:.1f} embeddings/second")
    print(f"\n{'='*60}\n")

def verify_embeddings():
    """Verify embedding generation results"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN embedding IS NOT NULL THEN 1 ELSE 0 END) as with_embeddings,
            SUM(CASE WHEN embedding IS NULL THEN 1 ELSE 0 END) as without_embeddings,
            ROUND(100.0 * SUM(CASE WHEN embedding IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as coverage_pct
        FROM gladiator_attack_patterns
    """)
    
    result = cursor.fetchone()
    total, with_emb, without_emb, coverage = result
    
    print("\n📊 EMBEDDING COVERAGE:")
    print(f"   Total patterns: {total}")
    print(f"   With embeddings: {with_emb}")
    print(f"   Without embeddings: {without_emb}")
    print(f"   Coverage: {coverage}%")
    
    # Test similarity search
    print("\n🔍 Testing Vector Similarity Search...")
    cursor.execute("""
        SELECT pattern_id, attack_type, 
               substring(description, 1, 60) as desc_preview
        FROM gladiator_attack_patterns
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> (
            SELECT embedding 
            FROM gladiator_attack_patterns 
            WHERE embedding IS NOT NULL 
            LIMIT 1
        )
        LIMIT 5
    """)
    
    print("\n   Similar patterns found:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]} - {row[2]}...")
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_embeddings()
    else:
        generate_embeddings(batch_size=50)
        verify_embeddings()

