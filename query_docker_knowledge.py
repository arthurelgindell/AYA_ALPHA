import psycopg2
import requests

# Query our embedded Docker documentation
conn = psycopg2.connect(
    host='localhost',
    database='aya_rag', 
    user='postgres',
    password='Power$$336633$$'
)

# Generate query embedding
query = "How to increase Docker Desktop memory allocation and resource limits on macOS"
embed_resp = requests.post(
    'http://localhost:8765/embed',
    json={'text': query}
)
query_embedding = embed_resp.json()['embedding']

# Semantic search in Docker docs
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        chunk_text,
        1 - (embedding <=> %s::vector) as similarity,
        metadata->>'title' as title
    FROM chunks
    WHERE source_table = 'docker_documentation'
    ORDER BY embedding <=> %s::vector
    LIMIT 5
""", (query_embedding, query_embedding))

print("=== DOCKER KNOWLEDGE FROM AYA RAG DATABASE ===\n")
for i, (text, sim, title) in enumerate(cursor.fetchall(), 1):
    print(f"[{i}] Similarity: {sim:.3f}")
    print(f"Title: {title}")
    print(f"Content: {text[:300]}...")
    print()

cursor.close()
conn.close()
