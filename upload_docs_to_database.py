#!/usr/bin/env python3
"""
Upload Agent Landing and JITM documentation to aya_rag database
This eliminates path confusion - database is single source of truth
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/Volumes/DATA/AYA/Agent_Turbo/core')
os.environ['DB_HOST'] = 'alpha.tail5f2bae.ts.net'

from postgres_connector import PostgreSQLConnector

def upload_documentation():
    """Upload all critical documentation to database"""
    
    print("="*80)
    print("UPLOADING DOCUMENTATION TO aya_rag DATABASE")
    print("="*80)
    print("This ensures single source of truth, no path confusion")
    print("")
    
    db = PostgreSQLConnector()
    
    try:
        # Create documentation table if not exists
        print("Creating documentation_content table...")
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS documentation_content (
                id SERIAL PRIMARY KEY,
                doc_name VARCHAR(500) NOT NULL UNIQUE,
                doc_type VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                file_path VARCHAR(1000),
                version VARCHAR(50),
                word_count INTEGER,
                line_count INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'
            );
            
            CREATE INDEX IF NOT EXISTS idx_documentation_doc_name ON documentation_content(doc_name);
            CREATE INDEX IF NOT EXISTS idx_documentation_doc_type ON documentation_content(doc_type);
            
            CREATE TRIGGER IF NOT EXISTS update_documentation_content_updated_at 
                BEFORE UPDATE ON documentation_content 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        """, fetch=False)
        print("✅ documentation_content table ready")
        print("")
        
        # Documents to upload
        docs_to_upload = [
            {
                'path': '/Volumes/DATA/AYA/AGENT_INITIALIZATION_LANDING.md',
                'type': 'agent_landing',
                'name': 'Agent Initialization Landing Context'
            },
            {
                'path': '/Volumes/DATA/JITM/JITM_MISSION_BRIEFING.md',
                'type': 'project_briefing',
                'name': 'JITM Mission Briefing'
            },
            {
                'path': '/Volumes/DATA/JITM/JITM_HA_CLUSTER_EVALUATION.md',
                'type': 'technical_analysis',
                'name': 'JITM HA Cluster Evaluation'
            },
            {
                'path': '/Volumes/DATA/AYA/POSTGRESQL_HA_CLUSTER_DEPLOYED.md',
                'type': 'deployment_report',
                'name': 'PostgreSQL HA Cluster Deployment'
            },
            {
                'path': '/Volumes/DATA/AYA/N8N_HA_CLUSTER_DEPLOYED.md',
                'type': 'deployment_report',
                'name': 'n8n HA Cluster Deployment'
            },
            {
                'path': '/Volumes/DATA/AYA/QUICK_REFERENCE.md',
                'type': 'reference',
                'name': 'AYA Quick Reference'
            },
            {
                'path': '/Volumes/DATA/AYA/README.md',
                'type': 'overview',
                'name': 'AYA Platform Overview'
            },
            {
                'path': '/Volumes/DATA/AYA/GLADIATOR_MISSION_BRIEFING.md',
                'type': 'project_briefing',
                'name': 'GLADIATOR Mission Briefing'
            },
            {
                'path': '/Volumes/DATA/JITM/README.md',
                'type': 'overview',
                'name': 'JITM Overview'
            },
            {
                'path': '/Volumes/DATA/JITM/JITM_DATABASE_UPDATE_SUMMARY.md',
                'type': 'technical_summary',
                'name': 'JITM Database Update Summary'
            }
        ]
        
        uploaded = 0
        skipped = 0
        
        for doc in docs_to_upload:
            doc_path = Path(doc['path'])
            
            if not doc_path.exists():
                print(f"⚠️  Skipping {doc['name']} - file not found at {doc['path']}")
                skipped += 1
                continue
            
            # Read file with error handling to prevent resource leaks
            try:
                content = doc_path.read_text(encoding='utf-8')
            except (IOError, OSError, UnicodeDecodeError) as e:
                print(f"❌ Error reading {doc['name']}: {e}")
                skipped += 1
                continue
                
            lines = content.split('\n')
            words = len(content.split())
            
            # Extract version with improved regex pattern
            version = 'N/A'
            import re
            for line in lines[:50]:  # Check more lines
                # Match patterns: "Version: 1.0", "**Version**: 1.0", "v1.0", etc
                version_match = re.search(r'(?:Version|version|v)[\s:*]*([0-9]+\.[0-9]+(?:\.[0-9]+)?)', line)
                if version_match:
                    version = version_match.group(1)
                    break
            
            print(f"Uploading: {doc['name']}")
            print(f"  Path: {doc['path']}")
            print(f"  Type: {doc['type']}")
            print(f"  Size: {len(content)} chars, {len(lines)} lines, {words} words")
            
            # Upload to database
            db.execute_query("""
                INSERT INTO documentation_content 
                (doc_name, doc_type, content, file_path, version, word_count, line_count, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (doc_name) 
                DO UPDATE SET
                    content = EXCLUDED.content,
                    file_path = EXCLUDED.file_path,
                    version = EXCLUDED.version,
                    word_count = EXCLUDED.word_count,
                    line_count = EXCLUDED.line_count,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW();
            """, params=(
                doc['name'],
                doc['type'],
                content,
                str(doc_path),
                version,
                words,
                len(lines),
                {
                    'uploaded_from': 'BETA',
                    'session_id': 'claude_code_planner_e40c8a2a',
                    'upload_date': datetime.now().isoformat(),
                    'file_size_bytes': len(content)
                }
            ), fetch=False)
            
            print(f"  ✅ Uploaded successfully")
            uploaded += 1
            print("")
        
        # Verification
        print("="*80)
        print("VERIFICATION")
        print("="*80)
        
        result = db.execute_query("""
            SELECT doc_name, doc_type, word_count, line_count, updated_at
            FROM documentation_content
            ORDER BY updated_at DESC
            LIMIT 15;
        """, fetch=True)
        
        print(f"\nDocumentation in database ({len(result)} recent entries):")
        for row in result:
            print(f"  • {row['doc_name']}")
            print(f"    Type: {row['doc_type']}, Words: {row['word_count']}, Lines: {row['line_count']}")
            print(f"    Updated: {row['updated_at']}")
        
        print("")
        print("="*80)
        print(f"✅ DOCUMENTATION UPLOAD COMPLETE")
        print("="*80)
        print(f"Uploaded: {uploaded} documents")
        print(f"Skipped: {skipped} (files not found)")
        print("")
        print("All documentation now in aya_rag database")
        print("No path confusion - database is source of truth!")
        print("")
        
        db.close_all_connections()
        return 0
        
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        db.close_all_connections()
        return 1

if __name__ == '__main__':
    sys.exit(upload_documentation())

