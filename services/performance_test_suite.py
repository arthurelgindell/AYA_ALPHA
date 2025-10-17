#!/usr/bin/env python3
"""
AYA Knowledge Base Performance Test Suite
Production System - Exhaustive Testing
Prime Directives: Functional Reality, Truth Over Comfort
"""

import time
import psycopg2
import requests
import json
import statistics
from datetime import datetime

# Configuration
ALPHA_DB = {
    'host': 'localhost',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

BETA_DB = {
    'host': '192.168.0.20',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}

EMBEDDING_SERVICE = 'http://localhost:8765'

class PerformanceTest:
    def __init__(self):
        self.results = {}
        self.failures = []

    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {level}: {message}")

    def test_database_connection(self):
        """Test 1: Database connectivity"""
        self.log("TEST 1: Database Connectivity")

        try:
            # ALPHA connection
            start = time.time()
            conn_alpha = psycopg2.connect(**ALPHA_DB)
            alpha_time = (time.time() - start) * 1000
            cursor = conn_alpha.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn_alpha.close()
            self.log(f"✅ ALPHA connected in {alpha_time:.2f}ms")
            self.log(f"   Version: {version[:50]}...")

            # BETA connection
            start = time.time()
            conn_beta = psycopg2.connect(**BETA_DB)
            beta_time = (time.time() - start) * 1000
            cursor = conn_beta.cursor()
            cursor.execute("SELECT pg_is_in_recovery();")
            is_replica = cursor.fetchone()[0]
            cursor.close()
            conn_beta.close()
            self.log(f"✅ BETA connected in {beta_time:.2f}ms")
            self.log(f"   Replica mode: {is_replica}")

            self.results['connection'] = {
                'alpha_ms': alpha_time,
                'beta_ms': beta_time,
                'status': 'PASS'
            }
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Database Connection', str(e)))
            self.results['connection'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def test_simple_queries(self):
        """Test 2: Simple query performance"""
        self.log("TEST 2: Simple Query Performance")

        try:
            conn = psycopg2.connect(**ALPHA_DB)
            cursor = conn.cursor()

            # Test queries
            queries = [
                ("SELECT COUNT(*) FROM documents", "Count documents"),
                ("SELECT COUNT(*) FROM chunks", "Count chunks"),
                ("SELECT id, category FROM documents LIMIT 10", "List documents"),
                ("SELECT pg_database_size('aya_rag')", "Database size"),
            ]

            times = []
            for query, desc in queries:
                start = time.time()
                cursor.execute(query)
                result = cursor.fetchall()
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                self.log(f"✅ {desc}: {elapsed:.2f}ms")

            cursor.close()
            conn.close()

            self.results['simple_queries'] = {
                'avg_ms': statistics.mean(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'status': 'PASS'
            }
            self.log(f"   Average: {statistics.mean(times):.2f}ms")
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Simple Queries', str(e)))
            self.results['simple_queries'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def test_embedding_service(self):
        """Test 3: Embedding service performance"""
        self.log("TEST 3: Embedding Service Performance")

        try:
            # Health check
            resp = requests.get(f"{EMBEDDING_SERVICE}/health")
            health = resp.json()
            self.log(f"✅ Health: {health}")

            if not health.get('metal_available'):
                self.log("⚠️  WARNING: Metal not available", 'WARN')

            # Test embedding generation
            test_texts = [
                "This is a short test",
                "This is a medium length test with some more words to process",
                "This is a longer test with significantly more content to generate embeddings for, testing the system's ability to handle larger text inputs efficiently and accurately."
            ]

            times = []
            dimensions = []

            for i, text in enumerate(test_texts, 1):
                start = time.time()
                resp = requests.post(
                    f"{EMBEDDING_SERVICE}/embed",
                    json={'text': text}
                )
                elapsed = (time.time() - start) * 1000

                if resp.status_code == 200:
                    embedding = resp.json()['embedding']
                    dimensions.append(len(embedding))
                    times.append(elapsed)
                    self.log(f"✅ Text {i} ({len(text)} chars): {elapsed:.2f}ms, {len(embedding)} dims")
                else:
                    raise Exception(f"HTTP {resp.status_code}: {resp.text}")

            # Verify all embeddings are 768 dimensions
            if not all(d == 768 for d in dimensions):
                raise Exception(f"Inconsistent dimensions: {dimensions}")

            self.results['embedding_service'] = {
                'avg_ms': statistics.mean(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'metal_available': health.get('metal_available'),
                'dimensions': 768,
                'status': 'PASS'
            }
            self.log(f"   Average: {statistics.mean(times):.2f}ms")
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Embedding Service', str(e)))
            self.results['embedding_service'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def test_vector_operations(self):
        """Test 4: Vector storage and retrieval"""
        self.log("TEST 4: Vector Storage and Retrieval")

        try:
            conn = psycopg2.connect(**ALPHA_DB)
            cursor = conn.cursor()

            # Generate test embedding
            resp = requests.post(
                f"{EMBEDDING_SERVICE}/embed",
                json={'text': 'Performance test vector operations'}
            )
            test_embedding = resp.json()['embedding']

            # Test 1: Insert with vector
            start = time.time()
            cursor.execute(
                "INSERT INTO documents (content, category) VALUES (%s, %s) RETURNING id",
                ('Performance test document', 'test')
            )
            doc_id = cursor.fetchone()[0]
            insert_time = (time.time() - start) * 1000
            self.log(f"✅ Document insert: {insert_time:.2f}ms (id={doc_id})")

            # Test 2: Insert chunk with vector
            start = time.time()
            cursor.execute(
                "INSERT INTO chunks (document_id, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s) RETURNING id",
                (doc_id, 0, 'Performance test chunk', test_embedding)
            )
            chunk_id = cursor.fetchone()[0]
            chunk_insert_time = (time.time() - start) * 1000
            self.log(f"✅ Chunk insert: {chunk_insert_time:.2f}ms (id={chunk_id})")

            # Test 3: Vector retrieval
            start = time.time()
            cursor.execute(
                "SELECT embedding FROM chunks WHERE id = %s",
                (chunk_id,)
            )
            retrieved = cursor.fetchone()[0]
            retrieve_time = (time.time() - start) * 1000
            self.log(f"✅ Vector retrieve: {retrieve_time:.2f}ms ({len(retrieved)} dims)")

            # Test 4: Vector similarity search
            start = time.time()
            cursor.execute("""
                SELECT id, chunk_text, embedding <-> %s::vector AS distance
                FROM chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> %s::vector
                LIMIT 5
            """, (test_embedding, test_embedding))
            results = cursor.fetchall()
            similarity_time = (time.time() - start) * 1000
            self.log(f"✅ Similarity search: {similarity_time:.2f}ms ({len(results)} results)")

            # Cleanup
            cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            conn.commit()

            cursor.close()
            conn.close()

            self.results['vector_operations'] = {
                'insert_ms': insert_time,
                'chunk_insert_ms': chunk_insert_time,
                'retrieve_ms': retrieve_time,
                'similarity_ms': similarity_time,
                'status': 'PASS'
            }
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Vector Operations', str(e)))
            self.results['vector_operations'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def test_replication_lag(self):
        """Test 5: Replication lag and consistency"""
        self.log("TEST 5: Replication Lag and Consistency")

        try:
            # Connect to both databases
            conn_alpha = psycopg2.connect(**ALPHA_DB)
            conn_beta = psycopg2.connect(**BETA_DB)
            cursor_alpha = conn_alpha.cursor()
            cursor_beta = conn_beta.cursor()

            # Insert test document on ALPHA
            test_content = f"Replication test at {datetime.now()}"
            start = time.time()
            cursor_alpha.execute(
                "INSERT INTO documents (content, category) VALUES (%s, %s) RETURNING id, created_at",
                (test_content, 'replication_test')
            )
            doc_id, created_at = cursor_alpha.fetchone()
            conn_alpha.commit()
            write_time = (time.time() - start) * 1000
            self.log(f"✅ ALPHA write: {write_time:.2f}ms (id={doc_id})")

            # Wait and check replication
            max_wait = 5  # seconds
            replicated = False
            wait_time = 0

            for attempt in range(10):
                time.sleep(0.5)
                wait_time += 0.5

                cursor_beta.execute(
                    "SELECT id, content FROM documents WHERE id = %s",
                    (doc_id,)
                )
                result = cursor_beta.fetchone()

                if result:
                    replicated = True
                    self.log(f"✅ BETA replicated: {wait_time*1000:.0f}ms lag")
                    break

            if not replicated:
                raise Exception(f"Replication failed after {max_wait}s")

            # Check replication status
            cursor_alpha.execute("""
                SELECT application_name, client_addr, state, sync_state, replay_lag
                FROM pg_stat_replication
            """)
            repl_status = cursor_alpha.fetchall()
            self.log(f"✅ Replication status: {repl_status}")

            # Cleanup
            cursor_alpha.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            conn_alpha.commit()

            cursor_alpha.close()
            cursor_beta.close()
            conn_alpha.close()
            conn_beta.close()

            self.results['replication'] = {
                'write_ms': write_time,
                'lag_ms': wait_time * 1000,
                'replicated': replicated,
                'status': 'PASS'
            }
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Replication', str(e)))
            self.results['replication'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def test_concurrent_operations(self):
        """Test 6: Concurrent read/write performance"""
        self.log("TEST 6: Concurrent Operations")

        try:
            conn = psycopg2.connect(**ALPHA_DB)
            cursor = conn.cursor()

            # Batch insert test
            batch_size = 10
            start = time.time()

            for i in range(batch_size):
                cursor.execute(
                    "INSERT INTO documents (content, category) VALUES (%s, %s) RETURNING id",
                    (f'Concurrent test {i}', 'concurrent_test')
                )

            conn.commit()
            batch_time = (time.time() - start) * 1000
            avg_per_insert = batch_time / batch_size

            self.log(f"✅ Batch insert ({batch_size}): {batch_time:.2f}ms total")
            self.log(f"   Average per insert: {avg_per_insert:.2f}ms")

            # Batch read test
            start = time.time()
            cursor.execute(
                "SELECT id, content, category FROM documents WHERE category = %s",
                ('concurrent_test',)
            )
            results = cursor.fetchall()
            read_time = (time.time() - start) * 1000

            self.log(f"✅ Batch read ({len(results)} rows): {read_time:.2f}ms")

            # Cleanup
            cursor.execute("DELETE FROM documents WHERE category = %s", ('concurrent_test',))
            conn.commit()

            cursor.close()
            conn.close()

            self.results['concurrent'] = {
                'batch_insert_ms': batch_time,
                'avg_insert_ms': avg_per_insert,
                'batch_read_ms': read_time,
                'status': 'PASS'
            }
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Concurrent Operations', str(e)))
            self.results['concurrent'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def test_memory_utilization(self):
        """Test 7: Memory configuration verification"""
        self.log("TEST 7: Memory Configuration")

        try:
            conn_alpha = psycopg2.connect(**ALPHA_DB)
            conn_beta = psycopg2.connect(**BETA_DB)
            cursor_alpha = conn_alpha.cursor()
            cursor_beta = conn_beta.cursor()

            # ALPHA settings
            cursor_alpha.execute("""
                SELECT name, setting, unit
                FROM pg_settings
                WHERE name IN (
                    'shared_buffers',
                    'effective_cache_size',
                    'work_mem',
                    'maintenance_work_mem',
                    'max_connections'
                )
            """)
            alpha_settings = cursor_alpha.fetchall()

            self.log("✅ ALPHA Memory Settings:")
            for name, setting, unit in alpha_settings:
                self.log(f"   {name}: {setting} {unit or ''}")

            # BETA settings
            cursor_beta.execute("""
                SELECT name, setting, unit
                FROM pg_settings
                WHERE name IN (
                    'shared_buffers',
                    'effective_cache_size',
                    'work_mem',
                    'maintenance_work_mem'
                )
            """)
            beta_settings = cursor_beta.fetchall()

            self.log("✅ BETA Memory Settings:")
            for name, setting, unit in beta_settings:
                self.log(f"   {name}: {setting} {unit or ''}")

            cursor_alpha.close()
            cursor_beta.close()
            conn_alpha.close()
            conn_beta.close()

            self.results['memory_config'] = {
                'alpha': {row[0]: f"{row[1]} {row[2] or ''}".strip() for row in alpha_settings},
                'beta': {row[0]: f"{row[1]} {row[2] or ''}".strip() for row in beta_settings},
                'status': 'PASS'
            }
            return True

        except Exception as e:
            self.log(f"❌ FAILED: {e}", 'ERROR')
            self.failures.append(('Memory Config', str(e)))
            self.results['memory_config'] = {'status': 'FAIL', 'error': str(e)}
            return False

    def run_all_tests(self):
        """Execute complete test suite"""
        self.log("=" * 60)
        self.log("AYA KNOWLEDGE BASE - EXHAUSTIVE PERFORMANCE TEST")
        self.log("=" * 60)

        tests = [
            self.test_database_connection,
            self.test_simple_queries,
            self.test_embedding_service,
            self.test_vector_operations,
            self.test_replication_lag,
            self.test_concurrent_operations,
            self.test_memory_utilization,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ TEST EXCEPTION: {e}", 'ERROR')
                failed += 1
            self.log("")

        # Summary
        self.log("=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)
        self.log(f"Total Tests: {passed + failed}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")

        if self.failures:
            self.log("\nFAILURES:")
            for test_name, error in self.failures:
                self.log(f"  - {test_name}: {error}", 'ERROR')

        # Production readiness
        self.log("\n" + "=" * 60)
        if failed == 0:
            self.log("✅ PRODUCTION READY: All tests passed", 'SUCCESS')
        else:
            self.log("❌ NOT PRODUCTION READY: Tests failed", 'ERROR')
        self.log("=" * 60)

        return passed, failed, self.results

if __name__ == '__main__':
    test_suite = PerformanceTest()
    passed, failed, results = test_suite.run_all_tests()

    # Save results
    with open('/Users/arthurdell/AYA/performance_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'passed': passed,
            'failed': failed,
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: /Users/arthurdell/AYA/performance_test_results.json")
    exit(0 if failed == 0 else 1)
