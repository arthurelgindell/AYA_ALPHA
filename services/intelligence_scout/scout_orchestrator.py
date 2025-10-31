#!/usr/bin/env python3
"""
Intelligence Scout Orchestrator - Main execution script
Coordinates crawler, processor, and integrator for complete intelligence gathering
"""

import sys
import argparse
from pathlib import Path
from typing import Dict

# Add services to path
sys.path.insert(0, str(Path(__file__).parent))

from scout_crawler import ScoutCrawler
from scout_processor import ScoutProcessor
from scout_integrator import ScoutIntegrator

class ScoutOrchestrator:
    """
    Orchestrates the complete intelligence gathering process
    """
    
    def __init__(self):
        """Initialize all components"""
        self.crawler = ScoutCrawler()
        self.processor = ScoutProcessor()
        self.integrator = ScoutIntegrator()
        print("✅ Intelligence Scout Orchestrator initialized")
    
    def process_queue_item(self, queue_id: int = None) -> Dict:
        """
        Process a single queue item through the complete pipeline
        
        Args:
            queue_id: Optional specific queue ID, otherwise gets next pending item
            
        Returns:
            Result statistics
        """
        # Get queue item
        queue_item = self.crawler.get_queue_item(queue_id)
        if not queue_item:
            return {'error': 'No pending queue items found'}
        
        queue_id = queue_item['id']
        url = queue_item['url']
        technology_name = queue_item['technology_name']
        max_pages = queue_item['max_pages']
        
        print(f"\n{'='*60}")
        print(f"📡 Processing: {technology_name}")
        print(f"🔗 URL: {url}")
        print(f"📄 Max Pages: {max_pages}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Start crawl
            print("Step 1: Starting crawl...")
            crawl_result = self.crawler.start_crawl(queue_id, url, max_pages)
            crawl_id = crawl_result['crawl_id']
            
            # Step 2: Monitor crawl progress
            print("Step 2: Monitoring crawl progress...")
            def progress_callback(state, completed, total):
                print(f"  Status: {state} | Progress: {completed}/{total}", end='\r')
            
            documents = self.crawler.monitor_crawl(queue_id, crawl_id, progress_callback)
            print(f"\n✅ Crawled {len(documents)} pages")
            
            # Step 3: Process documents
            print("Step 3: Processing documents...")
            processed_docs = []
            all_chunks = []
            source_urls = []
            
            for doc in documents:
                doc_data = self.crawler.extract_document_data(doc)
                source_urls.append(doc_data['url'])
                
                # Extract metadata
                metadata = self.processor.extract_metadata(
                    doc_data['url'],
                    doc_data['content'],
                    doc_data['title']
                )
                
                # Calculate importance
                importance = self.processor.calculate_importance(
                    doc_data['url'],
                    doc_data['content'],
                    doc_data['title']
                )
                
                doc_data['metadata'] = metadata
                doc_data['section_type'] = metadata['section_type']
                doc_data['importance_score'] = importance
                
                # Chunk content for embeddings
                chunks = self.processor.chunk_content(
                    doc_data.get('markdown') or doc_data.get('content', ''),
                    doc_data['url']
                )
                
                doc_data['chunks'] = chunks
                all_chunks.extend(chunks)
                processed_docs.append(doc_data)
            
            print(f"✅ Processed {len(processed_docs)} documents into {len(all_chunks)} chunks")
            
            # Step 4: Import to documentation table
            print("Step 4: Importing to documentation table...")
            table_stats = self.integrator.import_to_documentation_table(
                technology_name,
                processed_docs
            )
            print(f"✅ Imported {table_stats['imported']} documents to {table_stats['table_name']}")
            
            # Step 5: Import chunks to agent_knowledge
            print("Step 5: Importing chunks to agent_knowledge...")
            knowledge_ids = self.integrator.import_to_agent_knowledge(
                technology_name,
                all_chunks
            )
            print(f"✅ Created {len(knowledge_ids)} knowledge entries")
            
            # Step 6: Record results
            total_words = sum(doc.get('metadata', {}).get('word_count', 0) for doc in processed_docs)
            stats = {
                'imported': table_stats['imported'],
                'words_total': total_words,
                'chunks': len(all_chunks),
                'knowledge_entries': len(knowledge_ids)
            }
            
            result_id = self.integrator.record_results(
                queue_id,
                technology_name,
                table_stats['table_name'],
                stats,
                knowledge_ids
            )
            
            # Step 7: Update queue status
            self.crawler.update_queue_status(queue_id, 'completed')
            self.crawler.db.execute_query(
                """UPDATE intelligence_scout_queue 
                   SET pages_crawled = %s, completed_at = NOW()
                   WHERE id = %s""",
                (len(documents), queue_id),
                fetch='none'
            )
            
            print(f"\n{'='*60}")
            print(f"✅ COMPLETE: {technology_name}")
            print(f"📄 Pages: {len(documents)}")
            print(f"📚 Documents Imported: {table_stats['imported']}")
            print(f"💬 Chunks: {len(all_chunks)}")
            print(f"🧠 Knowledge Entries: {len(knowledge_ids)}")
            print(f"📊 Table: {table_stats['table_name']}")
            print(f"{'='*60}\n")
            
            return {
                'queue_id': queue_id,
                'result_id': result_id,
                'technology': technology_name,
                'pages_crawled': len(documents),
                'documents_imported': table_stats['imported'],
                'chunks': len(all_chunks),
                'knowledge_entries': len(knowledge_ids),
                'table_name': table_stats['table_name']
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ ERROR: {error_msg}")
            self.crawler.update_queue_status(queue_id, 'failed', error_message=error_msg)
            return {'error': error_msg, 'queue_id': queue_id}
    
    def queue_new_crawl(self, url: str, technology_name: str, 
                       priority: int = 5, max_pages: int = 1000) -> int:
        """
        Queue a new crawl
        
        Args:
            url: URL to crawl
            technology_name: Technology name
            priority: Priority (1-10)
            max_pages: Maximum pages to crawl
            
        Returns:
            Queue ID
        """
        result = self.crawler.db.execute_query(
            """INSERT INTO intelligence_scout_queue 
               (url, technology_name, priority, max_pages, status)
               VALUES (%s, %s, %s, %s, 'pending')
               RETURNING id""",
            (url, technology_name, priority, max_pages),
            fetch='one'
        )
        
        queue_id = result['id'] if result else None
        print(f"✅ Queued crawl: {technology_name} (ID: {queue_id})")
        return queue_id

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Intelligence Scout Orchestrator')
    parser.add_argument('action', choices=['process', 'queue', 'status'],
                       help='Action to perform')
    parser.add_argument('--queue-id', type=int, help='Specific queue ID to process')
    parser.add_argument('--url', help='URL to queue (for queue action)')
    parser.add_argument('--technology', help='Technology name (for queue action)')
    parser.add_argument('--priority', type=int, default=5, help='Priority 1-10 (for queue action)')
    parser.add_argument('--max-pages', type=int, default=1000, help='Max pages (for queue action)')
    
    args = parser.parse_args()
    
    orchestrator = ScoutOrchestrator()
    
    if args.action == 'process':
        result = orchestrator.process_queue_item(args.queue_id)
        print(json.dumps(result, indent=2))
    
    elif args.action == 'queue':
        if not args.url or not args.technology:
            print("Error: --url and --technology required for queue action")
            sys.exit(1)
        queue_id = orchestrator.queue_new_crawl(
            args.url, args.technology, args.priority, args.max_pages
        )
        print(f"Queue ID: {queue_id}")
    
    elif args.action == 'status':
        queue_item = orchestrator.crawler.get_queue_item(args.queue_id)
        if queue_item:
            print(json.dumps(dict(queue_item), indent=2, default=str))
        else:
            print("No queue item found")

if __name__ == '__main__':
    import json
    main()

