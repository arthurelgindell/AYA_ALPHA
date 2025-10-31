#!/usr/bin/env python3
"""
Intelligence Scout Integrator - Agent Turbo Knowledge Integration
Handles importing processed content into agent_knowledge and creating documentation tables
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
import json

# Add Agent Turbo to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Agent_Turbo' / 'core'))
from postgres_connector import PostgreSQLConnector
from agent_turbo import AgentTurbo

class ScoutIntegrator:
    """
    Integrates crawled content into Agent Turbo knowledge base
    """
    
    def __init__(self):
        """Initialize integrator with database and Agent Turbo"""
        self.db = PostgreSQLConnector()
        self.agent_turbo = AgentTurbo(silent=True)
        print("✅ Scout Integrator initialized")
    
    def create_documentation_table(self, technology_name: str) -> str:
        """
        Create technology-specific documentation table if it doesn't exist
        
        Args:
            technology_name: Name of technology (e.g., 'cursor', 'claude_api')
            
        Returns:
            Table name created
        """
        # Sanitize table name
        table_name = f"{technology_name.lower().replace('-', '_').replace(' ', '_')}_documentation"
        
        # Check if table exists
        exists = self.db.execute_query(
            """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )""",
            (table_name,),
            fetch='one'
        )
        
        if exists and exists['exists']:
            print(f"📋 Table {table_name} already exists")
            return table_name
        
        # Create table and indexes separately
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            description TEXT,
            content TEXT NOT NULL,
            markdown TEXT,
            metadata JSONB,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            word_count INTEGER,
            section_type VARCHAR(50),
            importance_score INTEGER DEFAULT 5
        )
        """
        
        self.db.execute_query(create_table_sql, fetch='none')
        
        # Create indexes separately
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_url ON {table_name}(url)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_title ON {table_name}(title)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_section ON {table_name}(section_type)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_metadata ON {table_name} USING GIN(metadata)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_content_fts ON {table_name} USING GIN(to_tsvector('english', content))"
        ]
        
        for index_sql in indexes:
            try:
                self.db.execute_query(index_sql, fetch='none')
            except Exception as e:
                # Index might already exist, continue
                pass
        print(f"✅ Created table: {table_name}")
        
        return table_name
    
    def import_to_documentation_table(self, technology_name: str, documents: List[Dict]) -> Dict:
        """
        Import documents into technology-specific documentation table
        
        Args:
            technology_name: Technology name
            documents: List of document dictionaries
            
        Returns:
            Import statistics
        """
        table_name = self.create_documentation_table(technology_name)
        
        imported = 0
        duplicates = 0
        errors = 0
        
        for doc in documents:
            try:
                url = doc.get('url', '')
                if not url:
                    errors += 1
                    continue
                
                # Check for duplicate URL
                existing = self.db.execute_query(
                    f"SELECT id FROM {table_name} WHERE url = %s",
                    (url,),
                    fetch='one'
                )
                
                if existing:
                    duplicates += 1
                    continue
                
                # Insert document
                insert_sql = f"""
                INSERT INTO {table_name} 
                (url, title, description, content, markdown, metadata, word_count, section_type, importance_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                word_count = len(doc.get('content', '').split())
                metadata_json = json.dumps(doc.get('metadata', {}))
                
                self.db.execute_query(
                    insert_sql,
                    (
                        url,
                        doc.get('title', ''),
                        doc.get('description', ''),
                        doc.get('content', ''),
                        doc.get('markdown', ''),
                        metadata_json,
                        word_count,
                        doc.get('section_type', 'general'),
                        doc.get('importance_score', 5)
                    ),
                    fetch='none'
                )
                
                imported += 1
                
            except Exception as e:
                errors += 1
                print(f"  ⚠️  Error importing {doc.get('url', 'unknown')}: {e}")
        
        return {
            'table_name': table_name,
            'imported': imported,
            'duplicates': duplicates,
            'errors': errors,
            'total': len(documents)
        }
    
    def import_to_agent_knowledge(self, technology_name: str, chunks: List[Dict], 
                                  scout_result_id: Optional[int] = None) -> List[int]:
        """
        Import content chunks into agent_knowledge with embeddings
        
        Args:
            technology_name: Technology name for source tracking
            chunks: List of content chunks (from processor)
            scout_result_id: Optional ID from intelligence_scout_results
            
        Returns:
            List of agent_knowledge IDs created
        """
        knowledge_ids = []
        imported = 0
        skipped = 0
        
        print(f"📚 Importing {len(chunks)} chunks to agent_knowledge...")
        
        for i, chunk in enumerate(chunks):
            try:
                content = chunk.get('content', '')
                if not content or len(content.strip()) < 50:
                    skipped += 1
                    continue
                
                # Prepare source URL for context
                source_url = chunk.get('url', '')
                if chunk.get('chunk_index', 0) > 0:
                    source_url += f"#chunk-{chunk['chunk_index']}"
                
                # Add knowledge via Agent Turbo
                result = self.agent_turbo.add(
                    content=content,
                    source_session=f"scout_{technology_name}",
                    knowledge_type='solution'
                )
                
                # Extract knowledge ID from result or query for it
                # AgentTurbo.add() returns a string message, so we need to query for the ID
                import hashlib
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                knowledge = self.db.execute_query(
                    """SELECT id FROM agent_knowledge 
                       WHERE content_hash = %s 
                       ORDER BY created_at DESC LIMIT 1""",
                    (content_hash,),
                    fetch='one'
                )
                
                if knowledge:
                    knowledge_id = knowledge['id']
                    knowledge_ids.append(knowledge_id)
                    
                    # Update with source tracking
                    self.db.execute_query(
                        """UPDATE agent_knowledge 
                           SET source_technology = %s, 
                               source_url = %s,
                               scout_import_id = %s
                           WHERE id = %s""",
                        (technology_name, source_url, scout_result_id, knowledge_id),
                        fetch='none'
                    )
                    
                    imported += 1
                    
                    if imported % 10 == 0:
                        print(f"  ✅ Imported {imported}/{len(chunks)} chunks...", end='\r')
                else:
                    skipped += 1
                    
            except Exception as e:
                skipped += 1
                print(f"  ⚠️  Error importing chunk {i}: {e}")
        
        print(f"\n✅ Imported {imported} chunks, skipped {skipped}")
        
        return knowledge_ids
    
    def record_results(self, queue_id: int, technology_name: str, table_name: str,
                      stats: Dict, knowledge_ids: List[int]) -> int:
        """
        Record import results in intelligence_scout_results table
        
        Args:
            queue_id: Queue ID that generated these results
            technology_name: Technology name
            table_name: Documentation table name
            stats: Import statistics
            knowledge_ids: List of agent_knowledge IDs
            
        Returns:
            Result record ID
        """
        result = self.db.execute_query(
            """INSERT INTO intelligence_scout_results
               (queue_id, technology_name, table_name, pages_imported, words_total,
                embeddings_generated, knowledge_ids, metadata)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                queue_id,
                technology_name,
                table_name,
                stats.get('imported', 0),
                stats.get('words_total', 0),
                len(knowledge_ids),
                knowledge_ids,
                json.dumps(stats)
            ),
            fetch='one'
        )
        
        return result['id'] if result else None
    
    def import_technical_documentation(self, technology_name: str, source_table: str) -> Dict:
        """
        Import existing documentation table into agent_knowledge
        
        Args:
            technology_name: Technology name
            source_table: Source documentation table name
            
        Returns:
            Import statistics
        """
        # Get all documents from source table
        docs = self.db.execute_query(
            f"""SELECT url, title, content, markdown, section_type 
                FROM {source_table} 
                ORDER BY importance_score DESC NULLS LAST, word_count DESC""",
            fetch='all'
        )
        
        total_imported = 0
        total_chunks = 0
        
        # Process in batches
        sys.path.insert(0, str(Path(__file__).parent))
        from scout_processor import ScoutProcessor
        processor = ScoutProcessor()
        
        for doc in docs:
            chunks = processor.chunk_content(
                doc.get('markdown') or doc.get('content', ''),
                doc.get('url', '')
            )
            
            if chunks:
                knowledge_ids = self.import_to_agent_knowledge(technology_name, chunks)
                total_imported += len(knowledge_ids)
                total_chunks += len(chunks)
        
        return {
            'technology': technology_name,
            'source_table': source_table,
            'documents_processed': len(docs),
            'chunks_created': total_chunks,
            'knowledge_entries': total_imported
        }

