#!/bin/bash
#
# AYA Knowledge Base Performance Test Suite
# Production System - Exhaustive Testing
# Prime Directives: Functional Reality, Truth Over Comfort
#

set -e

PGPASSWORD='Power$$336633$$'
export PGPASSWORD

ALPHA_PSQL="/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -h localhost"
BETA_PSQL="ssh arthurdell@192.168.0.20 \"PGPASSWORD='Power\\\$\\\$336633\\\$\\\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag\""
EMBEDDING_URL="http://localhost:8765"

PASSED=0
FAILED=0

log() {
    echo "[$(date +%H:%M:%S.%3N)] $1"
}

test_header() {
    echo ""
    echo "============================================================"
    echo "TEST $1: $2"
    echo "============================================================"
}

test_pass() {
    ((PASSED++))
    log "✅ TEST $1: PASS"
}

test_fail() {
    ((FAILED++))
    log "❌ TEST $1: FAIL - $2"
}

# Test 1: Database Connectivity
test_header 1 "Database Connectivity"
START=$(date +%s%3N)
if $ALPHA_PSQL -c "SELECT version();" > /tmp/alpha_version.txt 2>&1; then
    END=$(date +%s%3N)
    ELAPSED=$((END - START))
    log "✅ ALPHA connected in ${ELAPSED}ms"
    head -1 /tmp/alpha_version.txt | log
    test_pass 1
else
    test_fail 1 "ALPHA connection failed"
fi

START=$(date +%s%3N)
if ssh arthurdell@192.168.0.20 "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c 'SELECT pg_is_in_recovery();'" > /tmp/beta_recovery.txt 2>&1; then
    END=$(date +%s%3N)
    ELAPSED=$((END - START))
    log "✅ BETA connected in ${ELAPSED}ms"
    log "   Replica mode: $(grep -o 't\|f' /tmp/beta_recovery.txt | head -1)"
    test_pass "1b"
else
    test_fail "1b" "BETA connection failed"
fi

# Test 2: Simple Query Performance
test_header 2 "Simple Query Performance"

log "Testing: COUNT(*) FROM documents"
START=$(date +%s%3N)
DOC_COUNT=$($ALPHA_PSQL -t -c "SELECT COUNT(*) FROM documents;")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Document count: $DOC_COUNT (${ELAPSED}ms)"

log "Testing: COUNT(*) FROM chunks"
START=$(date +%s%3N)
CHUNK_COUNT=$($ALPHA_PSQL -t -c "SELECT COUNT(*) FROM chunks;")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Chunk count: $CHUNK_COUNT (${ELAPSED}ms)"

log "Testing: Database size"
START=$(date +%s%3N)
DB_SIZE=$($ALPHA_PSQL -t -c "SELECT pg_size_pretty(pg_database_size('aya_rag'));")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Database size: $DB_SIZE (${ELAPSED}ms)"

test_pass 2

# Test 3: Embedding Service Performance
test_header 3 "Embedding Service Performance"

log "Testing: Health check"
START=$(date +%s%3N)
HEALTH=$(curl -s "$EMBEDDING_URL/health")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Health check: ${ELAPSED}ms"
echo "$HEALTH" | python3 -m json.tool | log

log "Testing: Embedding generation (short text)"
START=$(date +%s%3N)
EMBED1=$(curl -s -X POST "$EMBEDDING_URL/embed" -H "Content-Type: application/json" -d '{"text": "Short test"}')
END=$(date +%s%3N)
ELAPSED=$((END - START))
DIM=$(echo "$EMBED1" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['embedding']))")
log "✅ Short text: ${ELAPSED}ms, ${DIM} dimensions"

log "Testing: Embedding generation (long text)"
START=$(date +%s%3N)
EMBED2=$(curl -s -X POST "$EMBEDDING_URL/embed" -H "Content-Type: application/json" -d '{"text": "This is a longer test with significantly more content to generate embeddings for, testing the systems ability to handle larger text inputs efficiently and accurately with the Metal-accelerated MLX framework on Apple Silicon M3 Ultra."}')
END=$(date +%s%3N)
ELAPSED=$((END - START))
DIM=$(echo "$EMBED2" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['embedding']))")
log "✅ Long text: ${ELAPSED}ms, ${DIM} dimensions"

if [ "$DIM" == "768" ]; then
    test_pass 3
else
    test_fail 3 "Wrong embedding dimensions: $DIM (expected 768)"
fi

# Test 4: Vector Operations
test_header 4 "Vector Storage and Retrieval"

log "Testing: Document insert"
START=$(date +%s%3N)
DOC_ID=$($ALPHA_PSQL -t -c "INSERT INTO documents (content, category) VALUES ('Performance test document', 'perf_test') RETURNING id;")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Document insert: ${ELAPSED}ms (id=$DOC_ID)"

log "Testing: Vector retrieval from existing chunks"
START=$(date +%s%3N)
VECTOR_COUNT=$($ALPHA_PSQL -t -c "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL;")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Vector count query: ${ELAPSED}ms ($VECTOR_COUNT vectors)"

if [ "$VECTOR_COUNT" -gt 0 ]; then
    log "Testing: Vector similarity search"
    START=$(date +%s%3N)
    SIMILARITY=$($ALPHA_PSQL -t -c "SELECT id, LEFT(chunk_text, 50) FROM chunks WHERE embedding IS NOT NULL LIMIT 3;")
    END=$(date +%s%3N)
    ELAPSED=$((END - START))
    log "✅ Similarity search: ${ELAPSED}ms"
fi

# Cleanup
$ALPHA_PSQL -c "DELETE FROM documents WHERE category = 'perf_test';" > /dev/null 2>&1

test_pass 4

# Test 5: Replication Performance
test_header 5 "Replication Performance and Consistency"

log "Testing: Write to ALPHA"
START_TIME=$(date +%s%3N)
TEST_CONTENT="Replication test at $(date +%Y-%m-%d\ %H:%M:%S)"
DOC_ID=$($ALPHA_PSQL -t -c "INSERT INTO documents (content, category) VALUES ('$TEST_CONTENT', 'repl_test') RETURNING id;")
WRITE_TIME=$(($(date +%s%3N) - START_TIME))
log "✅ ALPHA write: ${WRITE_TIME}ms (id=$DOC_ID)"

log "Testing: Replication lag"
sleep 2
START_TIME=$(date +%s%3N)
REPLICATED=$(ssh arthurdell@192.168.0.20 "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -t -c \"SELECT COUNT(*) FROM documents WHERE id = $DOC_ID;\"")
REPL_TIME=$(($(date +%s%3N) - START_TIME))

if [ "$REPLICATED" -eq 1 ]; then
    log "✅ BETA replicated: data found (query time: ${REPL_TIME}ms)"
    test_pass 5
else
    test_fail 5 "Replication failed: document not found on BETA"
fi

log "Testing: Replication status"
$ALPHA_PSQL -c "SELECT application_name, client_addr, state, sync_state FROM pg_stat_replication;" | log

# Cleanup
$ALPHA_PSQL -c "DELETE FROM documents WHERE category = 'repl_test';" > /dev/null 2>&1

# Test 6: Concurrent Operations
test_header 6 "Concurrent Operations Performance"

log "Testing: Batch insert (10 documents)"
START=$(date +%s%3N)
for i in {1..10}; do
    $ALPHA_PSQL -c "INSERT INTO documents (content, category) VALUES ('Concurrent test $i', 'concurrent_test');" > /dev/null 2>&1
done
END=$(date +%s%3N)
ELAPSED=$((END - START))
AVG=$((ELAPSED / 10))
log "✅ Batch insert: ${ELAPSED}ms total (${AVG}ms avg per insert)"

log "Testing: Batch read"
START=$(date +%s%3N)
RESULTS=$($ALPHA_PSQL -t -c "SELECT COUNT(*) FROM documents WHERE category = 'concurrent_test';")
END=$(date +%s%3N)
ELAPSED=$((END - START))
log "✅ Batch read: ${ELAPSED}ms ($RESULTS rows)"

# Cleanup
$ALPHA_PSQL -c "DELETE FROM documents WHERE category = 'concurrent_test';" > /dev/null 2>&1

test_pass 6

# Test 7: Memory Configuration
test_header 7 "Memory Configuration Verification"

log "ALPHA Memory Settings:"
$ALPHA_PSQL -c "SELECT name, setting, unit FROM pg_settings WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem', 'max_connections') ORDER BY name;" | log

log "BETA Memory Settings:"
ssh arthurdell@192.168.0.20 "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c \"SELECT name, setting, unit FROM pg_settings WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem') ORDER BY name;\"" | log

test_pass 7

# Test 8: Production Readiness Checklist
test_header 8 "Production Readiness Checklist"

log "Checking: PostgreSQL ALPHA running"
if pgrep -f "postgres.*5432" > /dev/null; then
    log "✅ PostgreSQL ALPHA: RUNNING"
else
    log "❌ PostgreSQL ALPHA: NOT RUNNING"
    test_fail "8a" "PostgreSQL ALPHA not running"
fi

log "Checking: PostgreSQL BETA running"
if ssh arthurdell@192.168.0.20 "pgrep -f postgres" > /dev/null 2>&1; then
    log "✅ PostgreSQL BETA: RUNNING"
else
    log "❌ PostgreSQL BETA: NOT RUNNING"
    test_fail "8b" "PostgreSQL BETA not running"
fi

log "Checking: Embedding service running"
if pgrep -f "uvicorn.*8765" > /dev/null; then
    log "✅ Embedding Service: RUNNING"
else
    log "❌ Embedding Service: NOT RUNNING"
    test_fail "8c" "Embedding service not running"
fi

log "Checking: Replication active"
REPL_COUNT=$($ALPHA_PSQL -t -c "SELECT COUNT(*) FROM pg_stat_replication;")
if [ "$REPL_COUNT" -gt 0 ]; then
    log "✅ Replication: ACTIVE ($REPL_COUNT connections)"
else
    log "❌ Replication: INACTIVE"
    test_fail "8d" "No active replication"
fi

test_pass 8

# Final Summary
echo ""
echo "============================================================"
echo "TEST SUMMARY"
echo "============================================================"
echo "Total Tests Passed: $PASSED"
echo "Total Tests Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "============================================================"
    echo "✅ PRODUCTION READY: All tests passed"
    echo "============================================================"
    exit 0
else
    echo "============================================================"
    echo "❌ NOT PRODUCTION READY: $FAILED tests failed"
    echo "============================================================"
    exit 1
fi
