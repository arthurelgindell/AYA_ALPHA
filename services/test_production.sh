#!/bin/bash
echo "===================================================================="
echo "AYA KNOWLEDGE BASE - PRODUCTION PERFORMANCE TEST"
echo "===================================================================="
echo ""

PGPASSWORD='Power$$336633$$'
export PGPASSWORD

echo "TEST 1: Database Connectivity"
echo "-------------------------------------------------------------------"
echo "ALPHA PostgreSQL:"
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT 'Connected to ' || version();" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "BETA PostgreSQL:"
ssh arthurdell@192.168.0.20 "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c \"SELECT 'Connected - Replica mode: ' || pg_is_in_recovery()::text;\"" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "TEST 2: Database Content & Performance"
echo "-------------------------------------------------------------------"
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT 
    'Documents' as table_name, 
    COUNT(*) as count,
    pg_size_pretty(pg_total_relation_size('documents')) as size
FROM documents
UNION ALL
SELECT 
    'Chunks' as table_name,
    COUNT(*) as count,
    pg_size_pretty(pg_total_relation_size('chunks')) as size
FROM chunks;
" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "TEST 3: Memory Configuration"
echo "-------------------------------------------------------------------"
echo "ALPHA Settings:"
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT 
    name,
    setting || ' ' || COALESCE(unit, '') as value
FROM pg_settings 
WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem', 'max_connections')
ORDER BY name;
" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "BETA Settings:"
ssh arthurdell@192.168.0.20 "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c \"
SELECT 
    name,
    setting || ' ' || COALESCE(unit, '') as value
FROM pg_settings 
WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem')
ORDER BY name;
\"" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "TEST 4: Embedding Service"
echo "-------------------------------------------------------------------"
curl -s http://localhost:8765/health | python3 -m json.tool

echo ""
echo "Generating test embedding..."
curl -s -X POST http://localhost:8765/embed -H 'Content-Type: application/json' -d '{"text": "Production performance test"}' | python3 -c 'import sys, json; d=json.load(sys.stdin); print(f"✅ Embedding generated: {len(d[\"embedding\"])} dimensions")'

echo ""
echo "TEST 5: Replication Status"
echo "-------------------------------------------------------------------"
/Library/PostgreSQL/18/bin/psql -U postgres -c "
SELECT 
    application_name,
    client_addr,
    state,
    sync_state,
    COALESCE(replay_lag::text, '0') as replay_lag
FROM pg_stat_replication;
" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "TEST 6: Write & Replication Test"
echo "-------------------------------------------------------------------"
echo "Writing test document to ALPHA..."
TEST_ID=$(/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -t -c "INSERT INTO documents (content, category) VALUES ('Production test $(date)', 'prod_test') RETURNING id;" | tr -d ' ')
echo "✅ Document written: ID=$TEST_ID"

echo "Waiting 2 seconds for replication..."
sleep 2

echo "Checking BETA..."
BETA_CHECK=$(ssh arthurdell@192.168.0.20 "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -t -c \"SELECT COUNT(*) FROM documents WHERE id = $TEST_ID;\"" | tr -d ' ')

if [ "$BETA_CHECK" = "1" ]; then
    echo "✅ Replication confirmed: Document found on BETA"
else
    echo "❌ Replication FAILED: Document not found on BETA"
fi

echo "Cleaning up..."
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "DELETE FROM documents WHERE category = 'prod_test';" > /dev/null 2>&1

echo ""
echo "TEST 7: Service Status"
echo "-------------------------------------------------------------------"
echo -n "ALPHA PostgreSQL: "
pgrep -f "postgres.*5432" > /dev/null && echo "✅ RUNNING" || echo "❌ NOT RUNNING"

echo -n "BETA PostgreSQL: "
ssh arthurdell@192.168.0.20 "pgrep -f postgres" > /dev/null 2>&1 && echo "✅ RUNNING" || echo "❌ NOT RUNNING"

echo -n "Embedding Service: "
pgrep -f "uvicorn.*8765" > /dev/null && echo "✅ RUNNING (PID=$(pgrep -f 'uvicorn.*8765'))" || echo "❌ NOT RUNNING"

echo ""
echo "===================================================================="
echo "PRODUCTION READINESS SUMMARY"
echo "===================================================================="
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT 
    (SELECT COUNT(*) FROM pg_stat_replication) as replication_connections,
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM chunks) as total_chunks,
    (SELECT setting FROM pg_settings WHERE name = 'effective_cache_size') as cache_size,
    (SELECT pg_size_pretty(pg_database_size('aya_rag'))) as db_size;
" 2>&1 | grep -v "INSERT\|DELETE"

echo ""
echo "===================================================================="
