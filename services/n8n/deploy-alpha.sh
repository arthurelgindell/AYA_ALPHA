#!/bin/bash
# Deploy n8n on ALPHA (stateless container, shared PostgreSQL state)

set -e

echo "=== Deploying n8n on ALPHA ==="

# Load encryption key
if [ ! -f "/Users/arthurdell/AYA/services/n8n/encryption_key.env" ]; then
    echo "ERROR: Encryption key not found at /Users/arthurdell/AYA/services/n8n/encryption_key.env"
    exit 1
fi

source /Users/arthurdell/AYA/services/n8n/encryption_key.env

# Stop existing container if running
docker stop n8n-alpha 2>/dev/null || true
docker rm n8n-alpha 2>/dev/null || true

# Deploy n8n container
docker run -d \
  --name n8n-alpha \
  --restart unless-stopped \
  -p 8080:5678 \
  -e DB_TYPE=postgresdb \
  -e DB_POSTGRESDB_HOST=alpha.tail5f2bae.ts.net \
  -e DB_POSTGRESDB_PORT=5432 \
  -e DB_POSTGRESDB_DATABASE=n8n_aya \
  -e DB_POSTGRESDB_USER=n8n_user \
  -e DB_POSTGRESDB_PASSWORD='Power$$336633$$' \
  -e N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY} \
  -e EXECUTIONS_MODE=queue \
  -e QUEUE_BULL_REDIS_HOST=alpha.tail5f2bae.ts.net \
  -e QUEUE_BULL_REDIS_PORT=6379 \
  -e N8N_HOST=n8n.aya.local \
  -e N8N_PORT=8080 \
  -e N8N_PROTOCOL=http \
  -e WEBHOOK_URL=http://n8n.aya.local:8080 \
  n8nio/n8n:latest

echo ""
echo "✅ n8n-alpha deployed"
echo "   Access: http://alpha.tail5f2bae.ts.net:8080"
echo "   Database: n8n_aya @ alpha.tail5f2bae.ts.net:5432"
echo "   Redis: alpha.tail5f2bae.ts.net:6379"
echo ""
echo "Waiting for startup..."
sleep 10

docker logs n8n-alpha 2>&1 | tail -5

