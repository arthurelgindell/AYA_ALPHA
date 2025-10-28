#!/usr/bin/env python3
"""
Enhanced PostgreSQL Connector with YugabyteDB Support
Supports both PostgreSQL and YugabyteDB with automatic failover

Created: October 28, 2025
"""

import psycopg2
from psycopg2 import pool
import psycopg2.extras
import os
import sys
import time
import random
from pathlib import Path

# Import YugabyteDB configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from config.yugabyte_config import (
        YUGABYTE_CONFIG, YUGABYTE_NODES, USE_YUGABYTE,
        ENABLE_FAILOVER, POOL_SETTINGS
    )
except ImportError:
    USE_YUGABYTE = False
    YUGABYTE_CONFIG = None

# Import pgvector if available
try:
    from pgvector.psycopg2 import register_vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    print("Warning: pgvector not installed. Vector operations will be limited.")

class PostgreSQLConnector:
    """
    Enhanced PostgreSQL/YugabyteDB connector with:
    - Support for both PostgreSQL and YugabyteDB
    - Automatic failover for YugabyteDB nodes
    - Connection pooling optimized for distributed systems
    - Vector support for both databases
    """
    
    def __init__(self, db_config=None, use_yugabyte=None):
        """
        Initialize connection pool for PostgreSQL or YugabyteDB.
        
        Args:
            db_config: Optional dict with connection parameters
            use_yugabyte: Override global USE_YUGABYTE setting
        """
        # Determine which database to use
        self.use_yugabyte = use_yugabyte if use_yugabyte is not None else USE_YUGABYTE
        
        # Set up configuration based on database type
        if self.use_yugabyte and YUGABYTE_CONFIG:
            print("🚀 Connecting to YugabyteDB distributed database...")
            self.db_config = db_config or YUGABYTE_CONFIG.copy()
            self.nodes = YUGABYTE_NODES
            self.current_node_index = 0
        else:
            print("🐘 Connecting to PostgreSQL...")
            self.db_config = db_config or {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': 5432,
                'database': 'aya_rag',
                'user': 'postgres',
                'password': os.getenv('PGPASSWORD', 'Power$$336633$$')
            }
            self.nodes = None
        
        # Initialize connection pool
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool with appropriate settings."""
        pool_config = POOL_SETTINGS if self.use_yugabyte else {
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
            if self.use_yugabyte and ENABLE_FAILOVER and self.nodes:
                print(f"⚠️  Failed to connect to node {self.current_node_index}, trying next...")
                self._failover()
            else:
                print(f"❌ Failed to create connection pool: {e}", file=sys.stderr)
                raise
    
    def _failover(self):
        """Try to connect to the next YugabyteDB node."""
        if not self.nodes or len(self.nodes) <= 1:
            raise psycopg2.Error("No alternative nodes available for failover")
        
        # Try each node
        original_index = self.current_node_index
        attempts = 0
        
        while attempts < len(self.nodes):
            self.current_node_index = (self.current_node_index + 1) % len(self.nodes)
            node = self.nodes[self.current_node_index]
            
            print(f"🔄 Attempting failover to node {self.current_node_index}: {node['host']}:{node['port']}")
            
            # Update configuration with new node
            self.db_config['host'] = node['host']
            self.db_config['port'] = node['port']
            
            try:
                self._init_pool()
                print(f"✅ Failover successful to node {self.current_node_index}")
                return
            except Exception as e:
                print(f"❌ Failover to node {self.current_node_index} failed: {e}")
                attempts += 1
        
        raise psycopg2.Error("All YugabyteDB nodes are unavailable")
    
    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self.pool.getconn()
        except psycopg2.pool.PoolError as e:
            if self.use_yugabyte and ENABLE_FAILOVER:
                self._failover()
                return self.pool.getconn()
            raise
    
    def return_connection(self, conn, close=False):
        """Return a connection to the pool."""
        if conn:
            self.pool.putconn(conn, close=close)
    
    def execute_query(self, query, params=None, fetch='all'):
        """
        Execute a query with automatic connection management.
        Enhanced with YugabyteDB retry logic.
        """
        conn = None
        max_retries = 3 if self.use_yugabyte else 1
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                conn = self.get_connection()
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                cursor.execute(query, params)
                
                if fetch == 'all':
                    result = cursor.fetchall()
                elif fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'many':
                    result = cursor.fetchmany()
                else:  # fetch == 'none'
                    result = None
                    conn.commit()
                
                cursor.close()
                return result
                
            except psycopg2.Error as e:
                if conn:
                    conn.rollback()
                
                # Check if this is a retriable error
                if attempt < max_retries - 1 and self.use_yugabyte:
                    if "conflict" in str(e).lower() or "retry" in str(e).lower():
                        time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                
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
    print("Testing PostgreSQL/YugabyteDB Connector...")
    
    # Test YugabyteDB connection
    print("\n1. Testing YugabyteDB:")
    yb_connector = PostgreSQLConnector(use_yugabyte=True)
    stats = yb_connector.get_stats()
    print(f"   Database: {stats['database']}")
    print(f"   Size: {stats['size']}")
    print(f"   Knowledge Entries: {stats['knowledge_entries']}")
    yb_connector.test_vector_search()
    yb_connector.close()
    
    # Test PostgreSQL connection
    print("\n2. Testing PostgreSQL:")
    pg_connector = PostgreSQLConnector(use_yugabyte=False)
    stats = pg_connector.get_stats()
    print(f"   Database: {stats['database']}")
    print(f"   Size: {stats['size']}")
    print(f"   Knowledge Entries: {stats['knowledge_entries']}")
    pg_connector.close()
