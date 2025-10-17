#!/usr/bin/env python3
"""
Crawl PostgreSQL 18 documentation using Firecrawl map + batch scrape
"""

from firecrawl import FirecrawlApp
import json
import sqlite3
from datetime import datetime
import time

# Initialize Firecrawl
api_key = "fc-b641c64dbb3b4962909c2f8f04c524ba"
app = FirecrawlApp(api_key=api_key)

# Target URL
base_url = "https://www.postgresql.org/docs/18/"

print(f"Starting PostgreSQL 18 documentation crawl")
print(f"Timestamp: {datetime.now().isoformat()}\n")

try:
    # Step 1: Map the site to get all URLs
    print("Step 1: Mapping site to discover all URLs...")
    map_result = app.map(base_url)

    # Extract URLs
    if hasattr(map_result, 'links'):
        urls = map_result.links
    elif isinstance(map_result, dict):
        urls = map_result.get('links', [])
    else:
        urls = []

    # Filter to only docs/18/ URLs
    urls = [url for url in urls if '/docs/18/' in url]

    print(f"✓ Found {len(urls)} documentation pages")

    if len(urls) == 0:
        print("No URLs found. Exiting.")
        exit(1)

    # Step 2: Batch scrape all URLs
    print(f"\nStep 2: Starting batch scrape of {len(urls)} pages...")

    batch_response = app.start_batch_scrape(
        urls,
        {
            'formats': ['markdown'],
            'onlyMainContent': True
        }
    )

    batch_id = batch_response.get('id') if isinstance(batch_response, dict) else batch_response.id
    print(f"Batch scrape started with ID: {batch_id}")
    print("Waiting for batch to complete...")

    # Poll for completion
    all_docs = []
    while True:
        status = app.get_batch_scrape_status(batch_id)
        state = status.status if hasattr(status, 'status') else status.get('status', 'unknown')
        total = status.total if hasattr(status, 'total') else status.get('total', 0)
        completed = status.completed if hasattr(status, 'completed') else status.get('completed', 0)

        print(f"Status: {state} | Progress: {completed}/{total}")

        if state == 'completed':
            # Get the data
            if hasattr(status, 'data'):
                all_docs = status.data
            elif isinstance(status, dict):
                all_docs = status.get('data', [])
            break
        elif state in ['failed', 'cancelled']:
            raise Exception(f"Batch scrape {state}")

        time.sleep(5)

    print(f"\n✓ Batch scrape completed!")
    print(f"Total pages scraped: {len(all_docs)}")

    # Step 3: Create SQLite database
    print("\nStep 3: Creating SQLite database...")
    db_path = '/Volumes/DATA/Databases/postgresql_18_docs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            content TEXT,
            markdown TEXT,
            metadata TEXT,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            word_count INTEGER,
            section_type TEXT
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON documentation(url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON documentation(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_section_type ON documentation(section_type)')

    # Insert data
    inserted_count = 0
    for doc in all_docs:
        # Convert to dict if needed
        if hasattr(doc, '__dict__'):
            doc_dict = {}
            for k, v in doc.__dict__.items():
                if not k.startswith('_'):
                    # Handle nested objects
                    if hasattr(v, '__dict__'):
                        doc_dict[k] = {kk: vv for kk, vv in v.__dict__.items() if not kk.startswith('_')}
                    else:
                        doc_dict[k] = v
        else:
            doc_dict = doc

        url = doc_dict.get('url', '')

        # Extract metadata safely
        metadata_obj = doc_dict.get('metadata', {})
        if hasattr(metadata_obj, '__dict__'):
            metadata = {k: v for k, v in metadata_obj.__dict__.items() if not k.startswith('_')}
        else:
            metadata = metadata_obj if isinstance(metadata_obj, dict) else {}

        title = metadata.get('title', '') or metadata.get('ogTitle', '') or doc_dict.get('title', '')
        content = doc_dict.get('content', '') or doc_dict.get('markdown', '')
        markdown = doc_dict.get('markdown', '')
        word_count = len(content.split()) if content else 0

        # Determine section type from URL
        section_type = 'general'
        if '/sql-' in url:
            section_type = 'sql'
        elif '/admin' in url:
            section_type = 'administration'
        elif '/tutorial' in url:
            section_type = 'tutorial'
        elif '/ref' in url or '/reference' in url:
            section_type = 'reference'
        elif '/app-' in url:
            section_type = 'applications'

        try:
            cursor.execute('''
                INSERT INTO documentation (url, title, content, markdown, metadata, word_count, section_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, content, markdown, json.dumps(metadata), word_count, section_type))
            inserted_count += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    # Generate statistics
    cursor.execute('SELECT COUNT(*) FROM documentation')
    total_docs = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(word_count) FROM documentation')
    total_words = cursor.fetchone()[0] or 0

    cursor.execute('SELECT section_type, COUNT(*) FROM documentation GROUP BY section_type ORDER BY COUNT(*) DESC')
    sections = cursor.fetchall()

    print(f"\n✓ Database created: {db_path}")
    print(f"✓ Documents inserted: {inserted_count}")
    print(f"✓ Total documents: {total_docs}")
    print(f"✓ Total words: {total_words:,}")
    print(f"\nSection breakdown:")
    for section, count in sections:
        print(f"  - {section}: {count} documents")

    # Step 4: Export PostgreSQL import SQL
    print("\nStep 4: Creating PostgreSQL import file...")
    sql_export_path = '/Volumes/DATA/Databases/postgresql_18_docs_import.sql'
    with open(sql_export_path, 'w', encoding='utf-8') as f:
        f.write("-- PostgreSQL 18 Documentation Import\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Total documents: {total_docs}\n")
        f.write(f"-- Total words: {total_words:,}\n\n")

        f.write("BEGIN;\n\n")

        f.write("CREATE TABLE IF NOT EXISTS documentation (\n")
        f.write("    id SERIAL PRIMARY KEY,\n")
        f.write("    url TEXT NOT NULL UNIQUE,\n")
        f.write("    title TEXT,\n")
        f.write("    content TEXT,\n")
        f.write("    markdown TEXT,\n")
        f.write("    metadata JSONB,\n")
        f.write("    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n")
        f.write("    word_count INTEGER,\n")
        f.write("    section_type TEXT\n")
        f.write(");\n\n")

        f.write("CREATE INDEX IF NOT EXISTS idx_doc_url ON documentation(url);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_doc_title ON documentation(title);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_doc_section ON documentation(section_type);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_doc_metadata ON documentation USING GIN(metadata);\n")
        f.write("CREATE INDEX IF NOT EXISTS idx_doc_content_fts ON documentation USING GIN(to_tsvector('english', content));\n\n")

        f.write("COMMIT;\n")

    print(f"✓ PostgreSQL schema saved: {sql_export_path}")

    # Save URL list
    url_list_path = '/Volumes/DATA/Databases/postgresql_18_urls.txt'
    with open(url_list_path, 'w') as f:
        for url in sorted(urls):
            f.write(url + '\n')

    print(f"✓ URL list saved: {url_list_path}")

    conn.close()
    print("\n✅ All tasks completed successfully!")

except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    raise
