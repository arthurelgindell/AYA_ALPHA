#!/bin/bash
# Deploy JITM to BETA
# Mac Studio M3 Ultra (256GB RAM, 16TB SSD)

set -e

echo "=========================================="
echo "JITM Deployment - BETA System"
echo "=========================================="
echo ""

# Check if running on BETA
HOSTNAME=$(hostname)
if [[ ! "$HOSTNAME" =~ "beta" ]]; then
    echo "⚠️  This script should be run on BETA"
    echo "Current hostname: $HOSTNAME"
    read -p "Continue anyway? (y/N): " confirm
    if [[ "$confirm" != "y" ]]; then
        exit 1
    fi
fi

# Verify BETA path structure
if [ ! -d "/Volumes/DATA" ]; then
    echo "❌ ERROR: /Volumes/DATA not found"
    echo "This script must run on BETA system with /Volumes/DATA"
    exit 1
fi

# Navigate to JITM directory (BETA path)
if [ -d "/Volumes/DATA/JITM" ]; then
    cd /Volumes/DATA/JITM
elif [ -d "$(dirname "$0")" ]; then
    cd "$(dirname "$0")"
else
    echo "❌ JITM directory not found"
    exit 1
fi

echo "📂 Working directory: $(pwd)"
echo "✅ Verified BETA path structure"
echo ""

# Check dependencies
echo "[1/7] Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ docker-compose not found"; exit 1; }
echo "✅ Docker available"
echo ""

# Create environment file if not exists
echo "[2/7] Setting up environment..."
if [ ! -f .env.beta ]; then
    echo "❌ .env.beta not found"
    echo "Creating from template..."
    cat > .env.beta << 'EOF'
SYSTEM_NAME=beta
SYSTEM_ID=2
JITM_API_PORT=8100
JITM_REDIS_PORT=6380
JITM_WORKERS=4
POSTGRES_HOST=alpha.tail5f2bae.ts.net
POSTGRES_PASSWORD=Power$$336633$$
AGENT_TURBO_URL=http://host.docker.internal:8765
N8N_WEBHOOK_URL=http://beta.tail5f2bae.ts.net:8080/webhook
PEER_SYSTEMS=alpha.tail5f2bae.ts.net:8100,beta.tail5f2bae.ts.net:8100
LOG_LEVEL=info
EOF
    echo "✅ Created .env.beta"
fi

cp .env.beta .env
echo "✅ Environment configured for BETA"
echo ""

# Stop existing containers
echo "[3/7] Stopping existing JITM containers..."
docker-compose down --remove-orphans 2>/dev/null || true
echo "✅ Cleanup complete"
echo ""

# Build images
echo "[4/7] Building Docker images..."
docker-compose build --no-cache
echo "✅ Images built"
echo ""

# Start services
echo "[5/7] Starting JITM services..."
docker-compose up -d
echo "✅ Services started"
echo ""

# Wait for health check
echo "[6/7] Waiting for API health check..."
sleep 5
for i in {1..30}; do
    if curl -sf http://localhost:8100/health > /dev/null 2>&1; then
        echo "✅ API is healthy"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done
echo ""

# Verify deployment
echo "[7/7] Verifying deployment..."
echo ""
echo "Container Status:"
docker-compose ps
echo ""
echo "API Health Check:"
curl -s http://localhost:8100/health | python3 -m json.tool || echo "Health check failed"
echo ""
echo "System Info:"
curl -s http://localhost:8100/system/info | python3 -m json.tool || echo "System info failed"
echo ""

echo "=========================================="
echo "✅ JITM Deployment Complete - BETA"
echo "=========================================="
echo ""
echo "Services:"
echo "  API:       http://localhost:8100"
echo "  Docs:      http://localhost:8100/docs"
echo "  Redis:     localhost:6380"
echo ""
echo "Logs:"
echo "  docker-compose logs -f jitm-api"
echo "  docker-compose logs -f jitm-worker"
echo ""
echo "Management:"
echo "  docker-compose ps          # Status"
echo "  docker-compose down        # Stop"
echo "  docker-compose restart     # Restart"
echo ""

