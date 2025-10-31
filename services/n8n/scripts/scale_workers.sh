#!/bin/bash
# Scale n8n workers dynamically based on queue depth or manual input
# Usage: ./scale_workers.sh <number_of_workers>

set -e

DOCKER_COMPOSE_FILE="/Users/arthurdell/N8N/docker/docker-compose.yml"
DOCKER_COMPOSE_DIR="/Users/arthurdell/N8N/docker"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <number_of_workers>"
    echo "Example: $0 5"
    exit 1
fi

WORKER_COUNT=$1

# Validate input
if ! [[ "$WORKER_COUNT" =~ ^[0-9]+$ ]]; then
    echo "Error: Worker count must be a positive integer"
    exit 1
fi

if [ "$WORKER_COUNT" -lt 0 ] || [ "$WORKER_COUNT" -gt 20 ]; then
    echo "Error: Worker count must be between 0 and 20"
    exit 1
fi

echo "=========================================="
echo "N8N WORKER SCALING"
echo "=========================================="
echo "Target worker count: $WORKER_COUNT"
echo ""

# Change to docker directory
cd "$DOCKER_COMPOSE_DIR"

# Scale workers
echo "Scaling n8n workers..."
docker-compose up -d --scale n8n-worker=$WORKER_COUNT --no-recreate

echo ""
echo "✅ Workers scaled to: $WORKER_COUNT"

# Update database worker status
echo ""
echo "Updating worker status in database..."
PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -c "
UPDATE n8n_workers 
SET status='active', last_heartbeat=NOW() 
WHERE worker_id LIKE 'n8n-worker-%';
" 2>/dev/null || echo "⚠️  Database update skipped (workers will self-register)"

echo ""
echo "=========================================="
echo "SCALING COMPLETE"
echo "=========================================="
echo "Active workers: $WORKER_COUNT"
echo "Check status: docker ps | grep n8n-worker"
echo "=========================================="

