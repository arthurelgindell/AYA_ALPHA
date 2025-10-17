#!/usr/bin/env python3
"""
Universal Firecrawl-based documentation crawler with proper data extraction
"""

from firecrawl import FirecrawlApp
import json
import sqlite3
from datetime import datetime
import time
import sys

# Initialize Firecrawl
api_key = "fc-b641c64dbb3b4962909c2f8f04c524ba"
app = FirecrawlApp(api_key=api_key)

def extract_document_data(doc):
    """Extract data from Firecrawl Document object"""
    # Get metadata (which contains the URL)
    metadata = doc.metadata if hasattr(doc, 'metadata') else None

    if metadata:
        url = metadata.url if hasattr(metadata, 'url') else ''
        title = metadata.title if hasattr(metadata, 'title') else ''
        description = metadata.description if hasattr(metadata, 'description') else ''
    else:
        url = ''
        title = ''
        description = ''

    # Get content
    markdown = doc.markdown if hasattr(doc, 'markdown') else ''
    html = doc.html if hasattr(doc, 'html') else ''
    content = markdown or html or ''

    # Get metadata as dict
    if metadata and hasattr(metadata, 'model_dump'):
        metadata_dict = metadata.model_dump()
    elif metadata and hasattr(metadata, 'dict'):
        metadata_dict = metadata.dict()
    else:
        metadata_dict = {}

    return {
        'url': url,
        'title': title,
        'description': description,
        'content': content,
        'markdown': markdown,
        'metadata': metadata_dict
    }

def crawl_site(base_url, db_name, table_name="documentation"):
    """Crawl a site and store in database"""

    print(f"Starting crawl of: {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    try:
        # Step 1: Start crawl
        print("Step 1: Starting comprehensive crawl...")
        crawl_response = app.start_crawl(
            base_url,
            limit=2000,
            max_discovery_depth=5,
            crawl_entire_domain=False,
            scrape_options={
                'formats': ['markdown'],
                'only_main_content': True
            }
        )

        crawl_id = crawl_response.get('id') if isinstance(crawl_response, dict) else crawl_response.id
        print(f"Crawl ID: {crawl_id}")
        print("Monitoring progress...")

        # Poll for completion
        all_docs = []
        while True:
            status = app.get_crawl_status(crawl_id)
            state = status.status if hasattr(status, 'status') else 'unknown'
            total = status.total if hasattr(status, 'total') else 0
            completed = status.completed if hasattr(status, 'completed') else 0

            print(f"  Status: {state} | Progress: {completed}/{total}", end='\r')

            if state == 'completed':
                if hasattr(status, 'data'):
                    all_docs = status.data
                print(f"\n✓ Crawl completed: {len(all_docs)} pages")
                break
            elif state in ['failed', 'cancelled']:
                raise Exception(f"Crawl {state}")

            time.sleep(5)

        # Step 2: Create database
        print("\nStep 2: Creating SQLite database...")
        db_path = f'/Volumes/DATA/Databases/{db_name}.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Drop and recreate table
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

        cursor.execute(f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                description TEXT,
                content TEXT,
                markdown TEXT,
                metadata TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                word_count INTEGER,
                section_type TEXT
            )
        ''')

        # Create indexes
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_url ON {table_name}(url)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_title ON {table_name}(title)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_section ON {table_name}(section_type)')

        # Step 3: Insert data
        print("\nStep 3: Processing and inserting documents...")
        inserted_count = 0
        error_count = 0

        for doc in all_docs:
            try:
                doc_data = extract_document_data(doc)

                url = doc_data['url']
                if not url:
                    error_count += 1
                    continue

                title = doc_data['title']
                description = doc_data['description']
                content = doc_data['content']
                markdown = doc_data['markdown']
                metadata = json.dumps(doc_data['metadata'])
                word_count = len(content.split()) if content else 0

                # Determine section type
                section_type = 'general'
                if '/docs/' in url or '/documentation' in url:
                    section_type = 'documentation'
                elif '/api/' in url:
                    section_type = 'api'
                elif '/blog' in url:
                    section_type = 'blog'
                elif '/tutorial' in url:
                    section_type = 'tutorial'
                elif '/guide' in url:
                    section_type = 'guide'
                elif '/reference' in url or '/ref' in url:
                    section_type = 'reference'

                cursor.execute(f'''
                    INSERT INTO {table_name} (url, title, description, content, markdown, metadata, word_count, section_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (url, title, description, content, markdown, metadata, word_count, section_type))
                inserted_count += 1

                if inserted_count % 50 == 0:
                    print(f"  Inserted {inserted_count} documents...", end='\r')

            except sqlite3.IntegrityError:
                error_count += 1
            except Exception as e:
                error_count += 1
                print(f"\n  Warning: {str(e)[:100]}")

        conn.commit()

        # Step 4: Generate statistics
        print(f"\n\n✓ Documents inserted: {inserted_count}")
        print(f"✓ Errors/Duplicates: {error_count}")

        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        total_docs = cursor.fetchone()[0]

        cursor.execute(f'SELECT SUM(word_count) FROM {table_name}')
        total_words = cursor.fetchone()[0] or 0

        cursor.execute(f'SELECT section_type, COUNT(*) FROM {table_name} GROUP BY section_type ORDER BY COUNT(*) DESC')
        sections = cursor.fetchall()

        cursor.execute(f'SELECT AVG(word_count) FROM {table_name}')
        avg_words = cursor.fetchone()[0] or 0

        print(f"\n✓ Total documents in DB: {total_docs}")
        print(f"✓ Total words: {total_words:,}")
        print(f"✓ Average words per page: {int(avg_words):,}")
        print(f"\nSection breakdown:")
        for section, count in sections:
            print(f"  - {section}: {count} documents")

        # Step 5: Export files
        print("\nStep 4: Exporting PostgreSQL import files...")

        # SQL schema
        sql_export_path = f'/Volumes/DATA/Databases/{db_name}_import.sql'
        with open(sql_export_path, 'w', encoding='utf-8') as f:
            f.write(f"-- {base_url} Documentation Import\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Total documents: {total_docs}\n")
            f.write(f"-- Total words: {total_words:,}\n")
            f.write(f"-- Source: {base_url}\n\n")

            f.write("BEGIN;\n\n")
            f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n\n")
            f.write(f"CREATE TABLE {table_name} (\n")
            f.write("    id SERIAL PRIMARY KEY,\n")
            f.write("    url TEXT NOT NULL UNIQUE,\n")
            f.write("    title TEXT,\n")
            f.write("    description TEXT,\n")
            f.write("    content TEXT,\n")
            f.write("    markdown TEXT,\n")
            f.write("    metadata JSONB,\n")
            f.write("    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n")
            f.write("    word_count INTEGER,\n")
            f.write("    section_type TEXT\n")
            f.write(");\n\n")

            f.write(f"CREATE INDEX idx_{table_name}_url ON {table_name}(url);\n")
            f.write(f"CREATE INDEX idx_{table_name}_title ON {table_name}(title);\n")
            f.write(f"CREATE INDEX idx_{table_name}_section ON {table_name}(section_type);\n")
            f.write(f"CREATE INDEX idx_{table_name}_metadata ON {table_name} USING GIN(metadata);\n")
            f.write(f"CREATE INDEX idx_{table_name}_content_fts ON {table_name} USING GIN(to_tsvector('english', content));\n\n")

            f.write("COMMIT;\n")

        # CSV export
        csv_export_path = f'/Volumes/DATA/Databases/{db_name}.csv'
        cursor.execute(f'SELECT url, title, description, content, markdown, metadata, word_count, section_type FROM {table_name}')
        import csv
        with open(csv_export_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            writer.writerow(['url', 'title', 'description', 'content', 'markdown', 'metadata', 'word_count', 'section_type'])
            writer.writerows(cursor.fetchall())

        # URL list
        url_list_path = f'/Volumes/DATA/Databases/{db_name}_urls.txt'
        cursor.execute(f'SELECT url FROM {table_name} ORDER BY url')
        with open(url_list_path, 'w') as f:
            for row in cursor.fetchall():
                f.write(row[0] + '\n')

        conn.close()

        print(f"✓ Database: {db_path}")
        print(f"✓ SQL schema: {sql_export_path}")
        print(f"✓ CSV export: {csv_export_path}")
        print(f"✓ URL list: {url_list_path}")

        print("\n✅ Crawl completed successfully!")
        return True

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 crawl_universal.py <url> <db_name> [table_name]")
        sys.exit(1)

    url = sys.argv[1]
    db_name = sys.argv[2]
    table_name = sys.argv[3] if len(sys.argv) > 3 else "documentation"

    crawl_site(url, db_name, table_name)
