#!/usr/bin/env python3
"""
Crawl Firecrawl.dev documentation using Firecrawl
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
base_url = "https://www.firecrawl.dev"

print(f"Starting Firecrawl.dev documentation crawl")
print(f"Timestamp: {datetime.now().isoformat()}\n")

try:
    # Step 1: Map the site to discover all URLs
    print("Step 1: Mapping site to discover all URLs...")
    map_result = app.map(base_url)

    # Extract URLs
    if hasattr(map_result, 'links'):
        all_links = map_result.links
    elif isinstance(map_result, dict):
        all_links = map_result.get('links', [])
    else:
        all_links = []

    # Filter to only firecrawl.dev URLs
    urls = [url for url in all_links if 'firecrawl.dev' in url and not url.endswith(('.png', '.jpg', '.gif', '.pdf'))]
    urls = list(set(urls))  # Remove duplicates

    print(f"✓ Found {len(urls)} pages")

    if len(urls) == 0:
        print("❌ No URLs found via map. Trying crawl approach...")
        # Fallback: use crawl
        crawl_response = app.start_crawl(
            base_url,
            limit=1000,
            max_discovery_depth=5
        )
        crawl_id = crawl_response.get('id') if isinstance(crawl_response, dict) else crawl_response.id
        print(f"Crawl started with ID: {crawl_id}")

        while True:
            status = app.get_crawl_status(crawl_id)
            state = status.status if hasattr(status, 'status') else 'unknown'
            total = status.total if hasattr(status, 'total') else 0
            completed = status.completed if hasattr(status, 'completed') else 0

            print(f"Status: {state} | Progress: {completed}/{total}", end='\r')

            if state == 'completed':
                if hasattr(status, 'data'):
                    all_docs = status.data
                else:
                    all_docs = []
                print(f"\n✓ Crawl completed: {len(all_docs)} pages")
                break
            elif state in ['failed', 'cancelled']:
                raise Exception(f"Crawl {state}")

            time.sleep(5)
    else:
        # Save URL list
        url_list_path = '/Volumes/DATA/Databases/firecrawl_dev_urls.txt'
        with open(url_list_path, 'w') as f:
            for url in sorted(urls):
                f.write(url + '\n')
        print(f"✓ URL list saved: {url_list_path}")

        # Step 2: Batch scrape all URLs (in chunks)
        print(f"\nStep 2: Batch scraping {len(urls)} pages...")

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
    db_path = '/Volumes/DATA/Databases/firecrawl_dev.db'
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
    error_count = 0

    for doc in all_docs:
        try:
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
            if not url:
                error_count += 1
                continue

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
            if '/docs/' in url:
                section_type = 'documentation'
            elif '/api/' in url:
                section_type = 'api'
            elif '/blog' in url:
                section_type = 'blog'
            elif '/pricing' in url:
                section_type = 'pricing'
            elif '/features' in url:
                section_type = 'features'

            cursor.execute('''
                INSERT INTO documentation (url, title, content, markdown, metadata, word_count, section_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, content, markdown, json.dumps(metadata), word_count, section_type))
            inserted_count += 1

        except sqlite3.IntegrityError:
            # Duplicate URL
            error_count += 1
        except Exception as e:
            error_count += 1
            print(f"\n  Warning: Error processing document: {str(e)[:100]}")

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
    print(f"✓ Errors/Duplicates: {error_count}")
    print(f"✓ Total documents in DB: {total_docs}")
    print(f"✓ Total words: {total_words:,}")
    print(f"✓ Average words per page: {int(avg_words):,}")
    print(f"\nSection breakdown:")
    for section, count in sections:
        print(f"  - {section}: {count} documents")

    # Step 4: Export PostgreSQL import SQL
    print("\nStep 4: Creating PostgreSQL import file...")
    sql_export_path = '/Volumes/DATA/Databases/firecrawl_dev_import.sql'
    with open(sql_export_path, 'w', encoding='utf-8') as f:
        f.write("-- Firecrawl.dev Documentation Import\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Total documents: {total_docs}\n")
        f.write(f"-- Total words: {total_words:,}\n")
        f.write(f"-- Source: https://www.firecrawl.dev\n\n")

        f.write("BEGIN;\n\n")

        f.write("-- Drop existing table if it exists\n")
        f.write("DROP TABLE IF EXISTS firecrawl_documentation CASCADE;\n\n")

        f.write("-- Create documentation table\n")
        f.write("CREATE TABLE firecrawl_documentation (\n")
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
        f.write("CREATE INDEX idx_firecrawl_url ON firecrawl_documentation(url);\n")
        f.write("CREATE INDEX idx_firecrawl_title ON firecrawl_documentation(title);\n")
        f.write("CREATE INDEX idx_firecrawl_section ON firecrawl_documentation(section_type);\n")
        f.write("CREATE INDEX idx_firecrawl_metadata ON firecrawl_documentation USING GIN(metadata);\n")
        f.write("CREATE INDEX idx_firecrawl_content_fts ON firecrawl_documentation USING GIN(to_tsvector('english', content));\n\n")

        f.write("COMMIT;\n")

    print(f"✓ PostgreSQL schema saved: {sql_export_path}")

    # Export CSV for PostgreSQL import
    csv_export_path = '/Volumes/DATA/Databases/firecrawl_dev.csv'
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
    if 'url_list_path' in locals():
        print(f"  4. {url_list_path}")

except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    raise
