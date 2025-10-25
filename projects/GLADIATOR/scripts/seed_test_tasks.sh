#!/bin/bash

# Seed Test Tasks for GLADIATOR Distributed Workers
# Creates test tasks in gladiator_execution_plan for workers to process

export PGPASSWORD='Power$$336633$$'

echo "=== Seeding Test Tasks for GLADIATOR Workers ==="
echo ""

# Check current task count
CURRENT_TASKS=$(/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -t -c "SELECT COUNT(*) FROM gladiator_execution_plan WHERE status = 'pending';")
echo "Current pending tasks: $CURRENT_TASKS"

# Insert 20 test tasks
echo "Inserting 20 test tasks..."

/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag <<EOF
INSERT INTO gladiator_execution_plan (week_number, phase, task_name, task_description, status, priority)
SELECT 
    0,
    'Phase 0',
    'Generate patterns ' || s || '-' || (s + 99),
    'Generate 100 attack patterns of mixed types',
    'pending',
    'high'
FROM generate_series(1, 2000, 100) s
LIMIT 20;
EOF

echo ""
echo "✅ Tasks seeded successfully!"
echo ""

# Show task summary
echo "=== Task Summary ==="
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT 
    status, 
    COUNT(*) as count
FROM gladiator_execution_plan
GROUP BY status
ORDER BY status;
"

echo ""
echo "=== Sample Tasks ==="
/Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "
SELECT 
    task_id, 
    task_name, 
    status, 
    priority
FROM gladiator_execution_plan
WHERE status = 'pending'
ORDER BY task_id DESC
LIMIT 5;
"

