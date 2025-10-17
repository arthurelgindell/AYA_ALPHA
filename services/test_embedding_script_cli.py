#!/usr/bin/env python3
"""
Test embedding generation on small sample
Uses PostgreSQL CLI tools to avoid psycopg2 import issues
"""

import requests
import json
import subprocess

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

LMSTUDIO_URL = "http://localhost:1234/v1/embeddings"
LMSTUDIO_MODEL = "text-embedding-nomic-embed-text-v1.5"

def run_psql(query):
    """Execute PostgreSQL query using psql CLI"""
    env = {"PGPASSWORD": DB_CONFIG['password']}
    cmd = [
        "/Library/PostgreSQL/18/bin/psql",
        "-U", DB_CONFIG['user'],
        "-d", DB_CONFIG['database'],
        "-t",  # Tuples only
        "-A",  # Unaligned output
        "-F", "\t",  # Tab separator
        "-c", query
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"   ❌ ERROR: {result.stderr}")
        return None
    return result.stdout.strip()

print("="*60)
print("EMBEDDING GENERATION TEST")
print("="*60)

# Test 1: LM Studio connection
print("\n1. Testing LM Studio connection...")
try:
    response = requests.post(
        LMSTUDIO_URL,
        json={"input": "test", "model": LMSTUDIO_MODEL},
        timeout=10
    )
    embedding = response.json()['data'][0]['embedding']
    print(f"   ✅ LM Studio OK (dimension: {len(embedding)})")
except Exception as e:
    print(f"   ❌ LM Studio ERROR: {e}")
    exit(1)

# Test 2: Database connection
print("\n2. Testing database connection...")
try:
    version = run_psql("SELECT version()")
    if version:
        print(f"   ✅ Database OK")
    else:
        print(f"   ❌ Database ERROR")
        exit(1)
except Exception as e:
    print(f"   ❌ Database ERROR: {e}")
    exit(1)

# Test 3: Fetch sample documents
print("\n3. Fetching sample documents (3 from postgresql_documentation)...")
try:
    result = run_psql("SELECT id, title, LEFT(content, 200) as content_preview FROM postgresql_documentation LIMIT 3")
    if not result:
        print("   ❌ Fetch ERROR: No results")
        exit(1)

    docs = []
    for line in result.split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            doc_id = parts[0]
            title = parts[1]
            preview = parts[2]
            docs.append((doc_id, title, preview))

    print(f"   ✅ Fetched {len(docs)} documents")
    for doc_id, title, preview in docs:
        print(f"      - ID {doc_id}: {title[:60]}...")
except Exception as e:
    print(f"   ❌ Fetch ERROR: {e}")
    exit(1)

# Test 4: Generate embeddings for sample
print("\n4. Generating embeddings for sample...")
try:
    texts = [f"{title}\n{preview}" for _, title, preview in docs]
    response = requests.post(
        LMSTUDIO_URL,
        json={"input": texts, "model": LMSTUDIO_MODEL},
        timeout=30
    )
    embeddings_data = response.json()
    embeddings = [item['embedding'] for item in embeddings_data['data']]
    print(f"   ✅ Generated {len(embeddings)} embeddings")
    print(f"      Dimension: {len(embeddings[0])}")
except Exception as e:
    print(f"   ❌ Embedding ERROR: {e}")
    exit(1)

# Test 5: Test chunk table structure
print("\n5. Testing chunk table structure...")
try:
    result = run_psql("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'chunks' ORDER BY ordinal_position")
    if not result:
        print("   ❌ Schema ERROR: No results")
        exit(1)

    columns = []
    for line in result.split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            columns.append((parts[0], parts[1]))

    print(f"   ✅ Chunks table has {len(columns)} columns:")
    for col_name, col_type in columns:
        print(f"      - {col_name}: {col_type}")
except Exception as e:
    print(f"   ❌ Schema ERROR: {e}")
    exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - Ready for production run")
print("="*60)
