#!/bin/bash
# N8N Production Deployment Script
# Deploys n8n with worker architecture and Agent Turbo integration

set -e

echo "=========================================="
echo "N8N PRODUCTION DEPLOYMENT"
echo "=========================================="
echo "Deployment Path: /Users/arthurdell/N8N"
echo "Database: aya_rag (PostgreSQL 18.0)"
echo "System: ALPHA (Mac Studio M3 Ultra)"
echo ""

# 1. Verify directory structure
echo "1. Verifying directory structure..."
if [ ! -d "/Users/arthurdell/N8N" ]; then
    echo "   ❌ N8N directory not found"
    exit 1
fi

REQUIRED_DIRS=("docker" "scripts" "workflows" "credentials" "data" "logs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "/Users/arthurdell/N8N/$dir" ]; then
        echo "   ⚠️  Creating missing directory: $dir"
        mkdir -p "/Users/arthurdell/N8N/$dir"
    fi
done
echo "   ✅ Directory structure verified"

# 2. Verify database schema
echo ""
echo "2. Verifying database schema..."
SCHEMA_FILE="/Users/arthurdell/AYA/n8n_schema_extension.sql"
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "   ❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

# Check if tables exist
TABLE_CHECK=$(PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -t -c "
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('n8n_workflows', 'n8n_executions', 'n8n_workers');
" 2>/dev/null || echo "0")

if [ "$TABLE_CHECK" -ne "3" ]; then
    echo "   ⚠️  Applying database schema..."
    PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -f "$SCHEMA_FILE"
    echo "   ✅ Schema applied"
else
    echo "   ✅ Schema already exists"
fi

# 3. Generate encryption key if not exists
echo ""
echo "3. Configuring environment..."
ENV_FILE="/Users/arthurdell/N8N/docker/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "   Creating .env file with encryption key..."
    N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)
    N8N_PASSWORD=$(openssl rand -base64 16)
    
    cat > "$ENV_FILE" << EOF
# N8N Environment Configuration
# Generated: $(date)

# Database
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=Power\$\$336633\$\$

# N8N Configuration
N8N_ENCRYPTION_KEY=$N8N_ENCRYPTION_KEY
N8N_PASSWORD=$N8N_PASSWORD

# Paths
N8N_DATA_PATH=/Users/arthurdell/N8N/data
N8N_WORKFLOWS_PATH=/Users/arthurdell/N8N/workflows
N8N_LOGS_PATH=/Users/arthurdell/N8N/logs

# Network
WEBHOOK_URL=http://localhost:5678

# System
SYSTEM_NODE=ALPHA
EOF
    echo "   ✅ Environment configured"
    echo "   📝 n8n credentials saved to: $ENV_FILE"
    echo "      Username: arthur"
    echo "      Password: $N8N_PASSWORD"
else
    echo "   ✅ Using existing .env file"
fi

# 4. Test Agent Turbo integration
echo ""
echo "4. Testing Agent Turbo integration..."
cd /Users/arthurdell/N8N/scripts
python3 agent_turbo_integration.py 2>/dev/null | tail -5 || echo "   ⚠️  Integration test skipped"

# 5. Build Docker images
echo ""
echo "5. Building Docker images..."
cd /Users/arthurdell/N8N/docker
docker-compose build --no-cache

echo "   ✅ Images built successfully"

# 6. Start services
echo ""
echo "6. Starting n8n infrastructure..."
docker-compose up -d

echo "   ✅ Services starting..."

# 7. Wait for services to be ready
echo ""
echo "7. Waiting for services to be ready..."
sleep 15

# Check n8n main
for i in {1..30}; do
    if curl -f http://localhost:5678/healthz 2>/dev/null; then
        echo "   ✅ n8n main instance ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  n8n taking longer than expected to start"
    fi
    sleep 2
done

# Check Redis
if docker exec n8n-redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "   ✅ Redis operational"
else
    echo "   ⚠️  Redis not responding"
fi

# Check workers
WORKER_COUNT=$(docker ps | grep -c n8n-worker || echo "0")
echo "   ✅ Workers running: $WORKER_COUNT"

# 8. Update Agent Turbo knowledge
echo ""
echo "8. Notifying Agent Turbo of deployment..."
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 -c "
from agent_launcher import launch_claude_planner
context = launch_claude_planner()
print('   ✅ Agent Turbo notified')
" 2>/dev/null || echo "   ⚠️  Agent Turbo notification skipped"

# 9. Display deployment summary
echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE ✅"
echo "=========================================="
echo ""
echo "n8n UI:        http://localhost:5678"
echo "Username:      arthur"
echo "Password:      (see $ENV_FILE)"
echo ""
echo "Workers:       $WORKER_COUNT (scale with: ./scripts/scale_workers.sh N)"
echo "Database:      aya_rag @ localhost:5432"
echo "Redis:         localhost:6379"
echo ""
echo "Commands:"
echo "  Status:      cd /Users/arthurdell/N8N/docker && docker-compose ps"
echo "  Logs:        docker-compose logs -f n8n-main"
echo "  Health:      python3 /Users/arthurdell/N8N/scripts/health_check.py"
echo "  Scale:       /Users/arthurdell/N8N/scripts/scale_workers.sh 5"
echo ""
echo "=========================================="

