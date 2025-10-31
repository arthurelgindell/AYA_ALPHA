#!/usr/bin/env python3
"""
PostgreSQL Connector for Agent Turbo
Connects to PostgreSQL 18 production database

Created: October 29, 2025
"""

import psycopg2
from psycopg2 import pool
import psycopg2.extras
import os
import sys
from pathlib import Path

# Import pgvector if available
try:
    from pgvector.psycopg2 import register_vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    print("Warning: pgvector not installed. Vector operations will be limited.")

class PostgreSQLConnector:
    """
    PostgreSQL connector for Agent Turbo.
    - Connection pooling for PostgreSQL 18
    - Vector support via pgvector extension
    """
    
    def __init__(self, db_config=None):
        """
        Initialize connection pool for PostgreSQL.
        
        Args:
            db_config: Optional dict with connection parameters
        """
        print("🐘 Connecting to PostgreSQL 18...")
        self.db_config = db_config or {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': 5432,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': os.getenv('PGPASSWORD', 'Power$$336633$$')
        }
        
        # Initialize connection pool
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool with appropriate settings."""
        pool_config = {
            'minconn': 2,
            'maxconn': 10
        }
        
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                **pool_config,
                **self.db_config
            )
            
            # Test connection and register vector type
            test_conn = self.pool.getconn()
            if HAS_PGVECTOR:
                register_vector(test_conn)
            
            # Test query
            cursor = test_conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✅ Connected to: {version}")
            cursor.close()
            self.pool.putconn(test_conn)
            
        except psycopg2.Error as e:
            print(f"❌ Failed to create connection pool: {e}", file=sys.stderr)
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        return self.pool.getconn()
    
    def return_connection(self, conn, close=False):
        """Return a connection to the pool."""
        if conn:
            self.pool.putconn(conn, close=close)
    
    def execute_query(self, query, params=None, fetch='all'):
        """
        Execute a query with automatic connection management.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute(query, params)
            
            # Check if this is a write operation (INSERT, UPDATE, DELETE)
            query_upper = query.strip().upper()
            is_write = query_upper.startswith(('INSERT', 'UPDATE', 'DELETE'))
            
            if fetch == 'all':
                result = cursor.fetchall()
            elif fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'many':
                result = cursor.fetchmany()
            else:  # fetch == 'none'
                result = None
            
            # CRITICAL FIX: Commit write operations regardless of fetch type
            if is_write:
                conn.commit()
            
            cursor.close()
            return result
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Query error: {e}", file=sys.stderr)
            raise
            
        finally:
            if conn:
                self.return_connection(conn)
    
    def test_vector_search(self, limit=3):
        """Test vector search functionality."""
        query = """
        SELECT id, substring(content, 1, 50) as content,
               octet_length(embedding::text) as embedding_size
        FROM agent_knowledge
        WHERE embedding IS NOT NULL
        LIMIT %s
        """
        
        try:
            results = self.execute_query(query, (limit,))
            print(f"\n🔍 Vector Search Test ({self.db_config['database']}):")
            for row in results:
                print(f"  ID: {row['id']}, Content: {row['content']}..., "
                      f"Embedding Size: {row['embedding_size']} bytes")
            return True
        except Exception as e:
            print(f"❌ Vector search test failed: {e}")
            return False
    
    def get_stats(self):
        """Get database statistics."""
        stats_query = """
        SELECT 
            current_database() as database,
            pg_size_pretty(pg_database_size(current_database())) as size,
            (SELECT COUNT(*) FROM agent_knowledge) as knowledge_entries,
            (SELECT COUNT(*) FROM agent_sessions) as sessions,
            (SELECT COUNT(*) FROM agent_tasks) as tasks,
            version() as version
        """
        
        return self.execute_query(stats_query, fetch='one')
    
    def close(self):
        """Close all connections in the pool."""
        if hasattr(self, 'pool') and self.pool:
            self.pool.closeall()
            print("🔌 Connection pool closed")

# Quick test when run directly
if __name__ == "__main__":
    print("Testing PostgreSQL Connector...")
    
    # Test PostgreSQL connection
    print("\n1. Testing PostgreSQL 18:")
    pg_connector = PostgreSQLConnector()
    stats = pg_connector.get_stats()
    print(f"   Database: {stats['database']}")
    print(f"   Size: {stats['size']}")
    print(f"   Knowledge entries: {stats['knowledge_entries']}")
    print(f"   Sessions: {stats['sessions']}")
    print(f"   Tasks: {stats['tasks']}")
    
    # Test vector search
    pg_connector.test_vector_search()
    
    pg_connector.close()
    print("\n✅ All tests passed!")