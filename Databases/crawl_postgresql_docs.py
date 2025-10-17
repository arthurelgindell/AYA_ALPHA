#!/usr/bin/env python3
"""
Crawl PostgreSQL 18 documentation using Firecrawl and prepare for PostgreSQL import
"""

from firecrawl import FirecrawlApp
import json
import sqlite3
from datetime import datetime
import os

# Initialize Firecrawl
api_key = "fc-b641c64dbb3b4962909c2f8f04c524ba"
app = FirecrawlApp(api_key=api_key)

# Target URL
url = "https://www.postgresql.org/docs/18/index.html"

print(f"Starting Firecrawl crawl of: {url}")
print(f"Timestamp: {datetime.now().isoformat()}")

try:
    # Start the crawl with full content extraction
    # Note: We're crawling the entire PostgreSQL 18 docs section
    crawl_response = app.start_crawl(
        url,
        limit=5000,
        max_discovery_depth=5,
        crawl_entire_domain=False,
        allow_subdomains=False,
        scrape_options={
            'formats': ['markdown'],
            'onlyMainContent': True
        }
    )

    crawl_id = crawl_response.get('id') if isinstance(crawl_response, dict) else crawl_response.id

    print(f"Crawl started with ID: {crawl_id}")
    print("Waiting for crawl to complete...")

    # Wait for completion
    import time
    while True:
        status = app.get_crawl_status(crawl_id)
        state = status.status if hasattr(status, 'status') else 'unknown'
        total = status.total if hasattr(status, 'total') else 0
        completed = status.completed if hasattr(status, 'completed') else 0

        print(f"Status: {state} | Progress: {completed}/{total}")

        if state == 'completed':
            # Get the final data
            crawl_result = {
                'status': state,
                'total': total,
                'completed': completed,
                'data': status.data if hasattr(status, 'data') else []
            }
            break
        elif state in ['failed', 'cancelled']:
            raise Exception(f"Crawl {state}")

        time.sleep(5)

    print(f"\n✓ Crawl completed successfully!")
    print(f"Total pages crawled: {len(crawl_result.get('data', []))}")

    # Save raw crawl data (convert Document objects to dicts)
    raw_output_path = '/Volumes/DATA/Databases/postgresql_18_docs_raw.json'

    # Convert data to serializable format
    serializable_data = {
        'status': crawl_result['status'],
        'total': crawl_result['total'],
        'completed': crawl_result['completed'],
        'data': []
    }

    for doc in crawl_result.get('data', []):
        if hasattr(doc, '__dict__'):
            doc_dict = {k: v for k, v in doc.__dict__.items() if not k.startswith('_')}
        else:
            doc_dict = doc
        serializable_data['data'].append(doc_dict)

    with open(raw_output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Raw data saved to: {raw_output_path}")

    # Create SQLite database for PostgreSQL import preparation
    db_path = '/Volumes/DATA/Databases/postgresql_18_docs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table with PostgreSQL-compatible structure
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

    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON documentation(url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON documentation(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_section_type ON documentation(section_type)')

    # Insert crawled data
    data = crawl_result.get('data', [])
    inserted_count = 0

    for page in data:
        # Handle both dict and object formats
        if hasattr(page, '__dict__'):
            page_dict = {k: v for k, v in page.__dict__.items() if not k.startswith('_')}
        else:
            page_dict = page

        url = page_dict.get('url', '')
        title = page_dict.get('title', '')
        content = page_dict.get('content', '') or page_dict.get('markdown', '')
        markdown = page_dict.get('markdown', '')
        metadata = json.dumps(page_dict.get('metadata', {}))
        word_count = len(content.split()) if content else 0

        # Determine section type from URL
        section_type = 'general'
        if '/sql-' in url:
            section_type = 'sql'
        elif '/admin' in url:
            section_type = 'administration'
        elif '/tutorial' in url:
            section_type = 'tutorial'
        elif '/ref' in url:
            section_type = 'reference'

        try:
            cursor.execute('''
                INSERT INTO documentation (url, title, content, markdown, metadata, word_count, section_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, content, markdown, metadata, word_count, section_type))
            inserted_count += 1
        except sqlite3.IntegrityError:
            # Skip duplicates
            pass

    conn.commit()

    # Generate statistics
    cursor.execute('SELECT COUNT(*) FROM documentation')
    total_docs = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(word_count) FROM documentation')
    total_words = cursor.fetchone()[0] or 0

    cursor.execute('SELECT section_type, COUNT(*) FROM documentation GROUP BY section_type')
    sections = cursor.fetchall()

    print(f"\n✓ Database created: {db_path}")
    print(f"✓ Documents inserted: {inserted_count}")
    print(f"✓ Total documents: {total_docs}")
    print(f"✓ Total words: {total_words:,}")
    print(f"\nSection breakdown:")
    for section, count in sections:
        print(f"  - {section}: {count} documents")

    # Export PostgreSQL import SQL
    sql_export_path = '/Volumes/DATA/Databases/postgresql_18_docs_import.sql'
    with open(sql_export_path, 'w', encoding='utf-8') as f:
        f.write("-- PostgreSQL 18 Documentation Import\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Total documents: {total_docs}\n\n")

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
        f.write("CREATE INDEX IF NOT EXISTS idx_doc_metadata ON documentation USING GIN(metadata);\n\n")

    print(f"✓ PostgreSQL import schema saved: {sql_export_path}")

    conn.close()
    print("\n✓ All tasks completed successfully!")

except Exception as e:
    print(f"\n✗ Error during crawl: {str(e)}")
    raise
