#!/usr/bin/env python3
"""
Crawl PostgreSQL 18 documentation using Firecrawl scrape with link extraction
"""

from firecrawl import FirecrawlApp
import json
import sqlite3
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse

# Initialize Firecrawl
api_key = "fc-b641c64dbb3b4962909c2f8f04c524ba"
app = FirecrawlApp(api_key=api_key)

# Target URL
index_url = "https://www.postgresql.org/docs/18/index.html"
base_url = "https://www.postgresql.org/docs/18/"

print(f"Starting PostgreSQL 18 documentation crawl")
print(f"Timestamp: {datetime.now().isoformat()}\n")

try:
    # Step 1: Scrape the index page to get all links
    print("Step 1: Scraping index page to extract all documentation links...")
    index_result = app.scrape(
        index_url,
        formats=['markdown', 'links'],
        only_main_content=False
    )

    # Extract links
    if hasattr(index_result, 'links'):
        all_links = index_result.links
    elif isinstance(index_result, dict):
        all_links = index_result.get('links', [])
    else:
        all_links = []

    # Get markdown content and extract links from it as well
    markdown_content = ''
    if hasattr(index_result, 'markdown'):
        markdown_content = index_result.markdown
    elif isinstance(index_result, dict):
        markdown_content = index_result.get('markdown', '')

    # Extract .html links from markdown
    html_links = re.findall(r'\(([\w\-]+\.html[^\)]*)\)', markdown_content)
    for link in html_links:
        full_url = urljoin(base_url, link.split('#')[0])
        if full_url not in all_links:
            all_links.append(full_url)

    # Filter to only docs/18/ HTML pages and remove duplicates
    urls = list(set([
        url for url in all_links
        if '/docs/18/' in url and url.endswith('.html') and '#' not in url
    ]))

    print(f"✓ Found {len(urls)} documentation pages")

    if len(urls) == 0:
        print("❌ No URLs found. Showing sample of links found:")
        print(all_links[:20])
        exit(1)

    # Save URL list
    url_list_path = '/Volumes/DATA/Databases/postgresql_18_urls.txt'
    with open(url_list_path, 'w') as f:
        for url in sorted(urls):
            f.write(url + '\n')
    print(f"✓ URL list saved: {url_list_path}")

    # Step 2: Batch scrape all URLs (in chunks due to API limits)
    print(f"\nStep 2: Batch scraping {len(urls)} pages...")

    # Firecrawl batch limit is typically 100-1000 URLs per batch
    chunk_size = 500
    all_docs = []

    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i+chunk_size]
        chunk_num = (i // chunk_size) + 1
        total_chunks = (len(urls) + chunk_size - 1) // chunk_size

        print(f"\nProcessing chunk {chunk_num}/{total_chunks} ({len(chunk)} URLs)...")

        batch_response = app.start_batch_scrape(
            chunk,
            formats=['markdown'],
            only_main_content=True
        )

        batch_id = batch_response.get('id') if isinstance(batch_response, dict) else batch_response.id
        print(f"Batch ID: {batch_id}")

        # Poll for completion
        while True:
            status = app.get_batch_scrape_status(batch_id)
            state = status.status if hasattr(status, 'status') else status.get('status', 'unknown')
            total = status.total if hasattr(status, 'total') else status.get('total', 0)
            completed = status.completed if hasattr(status, 'completed') else status.get('completed', 0)

            print(f"  Status: {state} | Progress: {completed}/{total}", end='\r')

            if state == 'completed':
                # Get the data
                if hasattr(status, 'data'):
                    chunk_docs = status.data
                elif isinstance(status, dict):
                    chunk_docs = status.get('data', [])
                else:
                    chunk_docs = []

                all_docs.extend(chunk_docs)
                print(f"\n  ✓ Chunk {chunk_num} completed: {len(chunk_docs)} pages scraped")
                break
            elif state in ['failed', 'cancelled']:
                print(f"\n  ✗ Chunk {chunk_num} {state}")
                break

            time.sleep(3)

    print(f"\n✓ Total pages scraped: {len(all_docs)}")

    # Step 3: Create SQLite database
    print("\nStep 3: Creating SQLite database...")
    db_path = '/Volumes/DATA/Databases/postgresql_18_docs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS documentation')

    # Create table
    cursor.execute('''
        CREATE TABLE documentation (
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
    cursor.execute('CREATE INDEX idx_url ON documentation(url)')
    cursor.execute('CREATE INDEX idx_title ON documentation(title)')
    cursor.execute('CREATE INDEX idx_section_type ON documentation(section_type)')

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
        elif '/datatype' in url:
            section_type = 'datatypes'
        elif '/functions' in url or '/func-' in url:
            section_type = 'functions'
        elif '/plpgsql' in url or '/plsql' in url:
            section_type = 'plpgsql'

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

    cursor.execute('SELECT AVG(word_count) FROM documentation')
    avg_words = cursor.fetchone()[0] or 0

    print(f"\n✓ Database created: {db_path}")
    print(f"✓ Documents inserted: {inserted_count}")
    print(f"✓ Total documents: {total_docs}")
    print(f"✓ Total words: {total_words:,}")
    print(f"✓ Average words per page: {int(avg_words):,}")
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
        f.write(f"-- Total words: {total_words:,}\n")
        f.write(f"-- Source: PostgreSQL 18 Official Documentation\n\n")

        f.write("BEGIN;\n\n")

        f.write("-- Drop existing table if it exists\n")
        f.write("DROP TABLE IF EXISTS documentation CASCADE;\n\n")

        f.write("-- Create documentation table\n")
        f.write("CREATE TABLE documentation (\n")
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

        f.write("-- Create indexes for performance\n")
        f.write("CREATE INDEX idx_doc_url ON documentation(url);\n")
        f.write("CREATE INDEX idx_doc_title ON documentation(title);\n")
        f.write("CREATE INDEX idx_doc_section ON documentation(section_type);\n")
        f.write("CREATE INDEX idx_doc_metadata ON documentation USING GIN(metadata);\n")
        f.write("CREATE INDEX idx_doc_content_fts ON documentation USING GIN(to_tsvector('english', content));\n\n")

        f.write("-- Note: Data import should be done using COPY command or pg_restore\n")
        f.write("-- Export SQLite data to CSV first, then use:\n")
        f.write("-- COPY documentation(url, title, content, markdown, metadata, word_count, section_type)\n")
        f.write("-- FROM '/path/to/postgresql_18_docs.csv' WITH (FORMAT csv, HEADER true);\n\n")

        f.write("COMMIT;\n")

    print(f"✓ PostgreSQL schema saved: {sql_export_path}")

    # Export CSV for PostgreSQL import
    csv_export_path = '/Volumes/DATA/Databases/postgresql_18_docs.csv'
    cursor.execute('SELECT url, title, content, markdown, metadata, word_count, section_type FROM documentation')
    import csv
    with open(csv_export_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(['url', 'title', 'content', 'markdown', 'metadata', 'word_count', 'section_type'])
        writer.writerows(cursor.fetchall())

    print(f"✓ CSV export saved: {csv_export_path}")

    conn.close()
    print("\n✅ All tasks completed successfully!")
    print(f"\nFiles created:")
    print(f"  1. {db_path}")
    print(f"  2. {sql_export_path}")
    print(f"  3. {csv_export_path}")
    print(f"  4. {url_list_path}")

except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    raise
