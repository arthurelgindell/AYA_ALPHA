#!/usr/bin/env python3
"""
Intelligence Scout Crawler - Enhanced Firecrawl Integration
Tracks progress in PostgreSQL database and supports incremental crawling
"""

from firecrawl import FirecrawlApp
import json
import sys
import os
from datetime import datetime
import time
from pathlib import Path

# Add Agent Turbo to path for database access
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Agent_Turbo' / 'core'))
from postgres_connector import PostgreSQLConnector

# Firecrawl API Key
FIRECRAWL_API_KEY = "fc-b641c64dbb3b4962909c2f8f04c524ba"

class ScoutCrawler:
    """
    Enhanced Firecrawl crawler with database progress tracking
    """
    
    def __init__(self):
        """Initialize crawler with Firecrawl API and database connection"""
        self.app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        self.db = PostgreSQLConnector()
        print("✅ Scout Crawler initialized")
    
    def extract_document_data(self, doc):
        """Extract data from Firecrawl Document object"""
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
    
    def start_crawl(self, queue_id: int, url: str, max_pages: int = 1000) -> dict:
        """
        Start a crawl and track it in the database
        
        Args:
            queue_id: ID from intelligence_scout_queue
            url: URL to crawl
            max_pages: Maximum pages to crawl
            
        Returns:
            dict with crawl_id and status
        """
        try:
            # Update queue status
            self.db.execute_query(
                """UPDATE intelligence_scout_queue 
                   SET status = 'crawling', started_at = NOW(), crawl_id = NULL
                   WHERE id = %s""",
                (queue_id,),
                fetch='none'  # UPDATE doesn't return rows
            )
            
            # Start Firecrawl crawl
            print(f"🚀 Starting crawl of: {url}")
            crawl_response = self.app.start_crawl(
                url,
                limit=max_pages,
                max_discovery_depth=5,
                crawl_entire_domain=False,
                scrape_options={
                    'formats': ['markdown'],
                    'only_main_content': True
                }
            )
            
            crawl_id = crawl_response.get('id') if isinstance(crawl_response, dict) else crawl_response.id
            
            # Update queue with crawl_id
            self.db.execute_query(
                """UPDATE intelligence_scout_queue 
                   SET crawl_id = %s WHERE id = %s""",
                (crawl_id, queue_id),
                fetch='none'  # UPDATE doesn't return rows
            )
            
            print(f"✅ Crawl started: {crawl_id}")
            return {'crawl_id': crawl_id, 'status': 'started'}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Crawl failed: {error_msg}")
            self.db.execute_query(
                """UPDATE intelligence_scout_queue 
                   SET status = 'failed', error_message = %s, completed_at = NOW()
                   WHERE id = %s""",
                (error_msg, queue_id),
                fetch='none'  # UPDATE doesn't return rows
            )
            raise
    
    def monitor_crawl(self, queue_id: int, crawl_id: str, progress_callback=None) -> list:
        """
        Monitor crawl progress and return documents when complete
        
        Args:
            queue_id: Queue ID for tracking
            crawl_id: Firecrawl crawl ID
            progress_callback: Optional callback(status, completed, total)
            
        Returns:
            List of document objects
        """
        print(f"📊 Monitoring crawl: {crawl_id}")
        all_docs = []
        max_attempts = 720  # 1 hour at 5 second intervals
        attempts = 0
        
        while attempts < max_attempts:
            try:
                status = self.app.get_crawl_status(crawl_id)
                state = status.status if hasattr(status, 'status') else 'unknown'
                total = status.total if hasattr(status, 'total') else 0
                completed = status.completed if hasattr(status, 'completed') else 0
                
                # Update database with progress
                self.db.execute_query(
                    """UPDATE intelligence_scout_queue 
                       SET pages_crawled = %s WHERE id = %s""",
                    (completed, queue_id),
                    fetch='none'
                )
                
                if progress_callback:
                    progress_callback(state, completed, total)
                
                print(f"  Status: {state} | Progress: {completed}/{total}", end='\r')
                
                if state == 'completed':
                    if hasattr(status, 'data'):
                        all_docs = status.data
                    elif hasattr(status, 'documents'):
                        all_docs = status.documents
                    print(f"\n✅ Crawl completed: {len(all_docs)} pages")
                    break
                elif state in ['failed', 'cancelled']:
                    error_msg = f"Crawl {state}"
                    self.db.execute_query(
                        """UPDATE intelligence_scout_queue 
                           SET status = 'failed', error_message = %s, completed_at = NOW()
                           WHERE id = %s""",
                        (error_msg, queue_id),
                        fetch='none'
                    )
                    raise Exception(error_msg)
                
                time.sleep(5)
                attempts += 1
                
            except Exception as e:
                error_msg = str(e)
                print(f"\n❌ Monitoring error: {error_msg}")
                self.db.execute_query(
                    """UPDATE intelligence_scout_queue 
                       SET status = 'failed', error_message = %s, completed_at = NOW()
                       WHERE id = %s""",
                    (error_msg, queue_id)
                )
                raise
        
        if attempts >= max_attempts:
            raise Exception("Crawl monitoring timeout")
        
        return all_docs
    
    def get_queue_item(self, queue_id: int = None) -> dict:
        """
        Get next pending item from queue or specific item
        
        Args:
            queue_id: Optional specific queue ID, otherwise gets highest priority pending
            
        Returns:
            Queue item dict or None
        """
        if queue_id:
            result = self.db.execute_query(
                """SELECT * FROM intelligence_scout_queue WHERE id = %s""",
                (queue_id,),
                fetch='one'
            )
        else:
            result = self.db.execute_query(
                """SELECT * FROM intelligence_scout_queue 
                   WHERE status = 'pending' 
                   ORDER BY priority DESC, created_at ASC 
                   LIMIT 1""",
                fetch='one'
            )
        
        return dict(result) if result else None
    
    def update_queue_status(self, queue_id: int, status: str, **kwargs):
        """Update queue item status and optional fields"""
        updates = [f"status = '{status}'"]
        params = []
        
        if 'error_message' in kwargs:
            updates.append("error_message = %s")
            params.append(kwargs['error_message'])
        
        if 'pages_crawled' in kwargs:
            updates.append("pages_crawled = %s")
            params.append(kwargs['pages_crawled'])
        
        if status == 'completed':
            updates.append("completed_at = NOW()")
        elif status == 'processing':
            updates.append("status = 'processing'")
        
        params.append(queue_id)
        
        query = f"""UPDATE intelligence_scout_queue 
                    SET {', '.join(updates)} 
                    WHERE id = %s"""
        
        self.db.execute_query(query, tuple(params), fetch='none')

