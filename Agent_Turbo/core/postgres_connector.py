#!/usr/bin/env python3
"""
PostgreSQL Connector for Agent Turbo
High-performance connection pooling for aya_rag database

Prime Directives Compliance:
- Directive #1: FUNCTIONAL REALITY ONLY - All methods query actual PostgreSQL
- Directive #11: NO THEATRICAL WRAPPERS - Real database connections, real queries
"""

import psycopg2
from psycopg2 import pool
import psycopg2.extras
import os
import sys
from pgvector.psycopg2 import register_vector

class PostgreSQLConnector:
    """
    High-performance PostgreSQL connector with connection pooling.
    
    Features:
    - ThreadedConnectionPool for concurrent operations
    - Automatic connection management
    - RealDictCursor for easy result access
    - Error handling with detailed messages
    """
    
    def __init__(self, db_config=None):
        """
        Initialize connection pool.
        
        Args:
            db_config: Optional dict with connection parameters
                      Defaults to aya_rag database on localhost
        """
        self.db_config = db_config or {
            'host': os.getenv('DB_HOST', 'alpha.tail5f2bae.ts.net,beta.tail5f2bae.ts.net'),  # Patroni HA cluster
            'port': 5432,
            'database': 'aya_rag',
            'user': 'postgres',
            'password': os.getenv('PGPASSWORD', 'Power$$336633$$'),
            'target_session_attrs': 'read-write'  # Patroni: auto-connect to primary for writes
        }
        
        try:
            # Connection pool for performance
            # min=2 ensures connections are ready
            # max=10 allows concurrent agent sessions
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                **self.db_config
            )
            
            # Register pgvector type with psycopg2
            test_conn = self.pool.getconn()
            register_vector(test_conn)
            self.pool.putconn(test_conn)
            
        except psycopg2.Error as e:
            print(f"❌ Failed to create connection pool: {e}", file=sys.stderr)
            raise
    
    def get_connection(self):
        """
        Get connection from pool and register pgvector.
        
        Returns:
            psycopg2.connection: Database connection with pgvector registered
        """
        try:
            conn = self.pool.getconn()
            # Ensure connection is in a clean state
            conn.rollback()  # Clear any pending transactions
            # Register pgvector on each connection from pool
            register_vector(conn)
            return conn
        except psycopg2.pool.PoolError as e:
            print(f"❌ Connection pool exhausted: {e}", file=sys.stderr)
            raise
    
    def release_connection(self, conn):
        """
        Return connection to pool.
        
        Args:
            conn: Connection to release
        """
        if conn:
            self.pool.putconn(conn)
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute query with automatic connection management.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch: Whether to fetch results (False for INSERT/UPDATE/DELETE)
        
        Returns:
            list: Query results as list of dicts (if fetch=True)
            None: If fetch=False
        
        Raises:
            psycopg2.Error: On database errors
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                
                if fetch:
                    # Fetch all results
                    results = cur.fetchall()
                    # Commit if this is a write operation with RETURNING
                    # (INSERT/UPDATE/DELETE with RETURNING clause)
                    query_upper = query.strip().upper()
                    if query_upper.startswith(('INSERT', 'UPDATE', 'DELETE')):
                        conn.commit()
                    # Convert RealDictRow to regular dict for easier use
                    return [dict(row) for row in results]
                else:
                    # Commit for write operations
                    query_upper = query.strip().upper()
                    if query_upper.startswith(('INSERT', 'UPDATE', 'DELETE')):
                        conn.commit()
                    return None
                    
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Query failed: {e}", file=sys.stderr)
            print(f"   Query: {query[:100]}...", file=sys.stderr)
            raise
        finally:
            if conn:
                # Ensure connection is in clean state before returning to pool
                try:
                    conn.commit()  # Commit any pending transaction
                except:
                    conn.rollback()  # Rollback on commit failure
                self.release_connection(conn)
    
    def execute_many(self, query, params_list):
        """
        Execute same query with multiple parameter sets (batch insert).
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples/dicts
        
        Returns:
            int: Number of rows affected
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
                rowcount = cur.rowcount
                conn.commit()
                return rowcount
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Batch query failed: {e}", file=sys.stderr)
            raise
        finally:
            if conn:
                self.release_connection(conn)
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
    
    def get_pool_status(self):
        """
        Get connection pool status.
        
        Returns:
            dict: Pool statistics
        """
        return {
            'minconn': self.pool.minconn,
            'maxconn': self.pool.maxconn,
            'closed': self.pool.closed
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close all connections."""
        self.close_all_connections()
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.close_all_connections()
        except:
            pass


# Verification functions (for testing)
def verify_connector():
    """
    Verify PostgreSQL connector is working.
    
    Prime Directive #1: Test actual database, not mocks.
    """
    print("🔍 Verifying PostgreSQL Connector...")
    
    try:
        # Test 1: Connection creation
        db = PostgreSQLConnector()
        print("✅ Connection pool created")
        
        # Test 2: Simple query
        result = db.execute_query('SELECT 1 as test', fetch=True)
        assert result[0]['test'] == 1, "Query result mismatch"
        print(f"✅ Query result: {result}")
        
        # Test 3: Pool status
        status = db.get_pool_status()
        print(f"✅ Pool config: {status['minconn']}-{status['maxconn']} connections")
        
        # Test 4: Real database query
        result = db.execute_query('SELECT COUNT(*) as count FROM system_nodes', fetch=True)
        print(f"✅ System nodes: {result[0]['count']}")
        
        # Test 5: Table existence check
        result = db.execute_query("""
            SELECT COUNT(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'agent_%'
        """, fetch=True)
        table_count = result[0]['table_count']
        assert table_count == 5, f"Expected 5 agent tables, found {table_count}"
        print(f"✅ Agent tables: {table_count}")
        
        db.close_all_connections()
        print("\n✅ PostgreSQL Connector: VERIFIED AND OPERATIONAL")
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Run verification when executed directly
    success = verify_connector()
    sys.exit(0 if success else 1)

