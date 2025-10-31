#!/bin/bash
# Deploy Grafana Dashboard System on BETA node
# Usage: ./deploy_beta.sh

set -e

echo "========================================"
echo "AYA Grafana Dashboard - BETA Deployment"
echo "========================================"
echo

# Verify we're on BETA
HOSTNAME=$(hostname)
if [[ ! "$HOSTNAME" =~ beta ]]; then
    echo "⚠️  Warning: This script is intended for BETA node"
    echo "Current hostname: $HOSTNAME"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Python found: $(python3 --version)"
echo

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd /Volumes/DATA/AYA/services/grafana/exporters
python3 -m pip install --user -r requirements.txt
echo "✅ Dependencies installed"
echo

# Stop existing containers (if any)
echo "🛑 Stopping existing containers..."
docker-compose -f ../docker-compose-beta.yml down 2>/dev/null || true
echo

# Pull latest images
echo "📥 Pulling Docker images..."
docker-compose -f ../docker-compose-beta.yml pull
echo "✅ Images pulled"
echo

# Start services
echo "🚀 Starting Grafana stack..."
cd /Volumes/DATA/AYA/services/grafana
docker-compose -f docker-compose-beta.yml up -d
echo "✅ Grafana stack started"
echo

# Wait for Grafana to be ready
echo "⏳ Waiting for Grafana to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health > /dev/null; then
        echo "✅ Grafana is ready!"
        break
    fi
    echo -n "."
    sleep 2
done
echo

# Start custom exporters
echo "🚀 Starting custom exporters..."

# Start AYA metrics exporter
pkill -f aya_metrics_exporter.py 2>/dev/null || true
nohup python3 /Volumes/DATA/AYA/services/grafana/exporters/aya_metrics_exporter.py > /tmp/aya_metrics_exporter.log 2>&1 &
echo "✅ AYA metrics exporter started (port 9200)"

# Start Tailscale exporter
pkill -f tailscale_exporter.py 2>/dev/null || true
nohup python3 /Volumes/DATA/AYA/services/grafana/exporters/tailscale_exporter.py > /tmp/tailscale_exporter.log 2>&1 &
echo "✅ Tailscale exporter started (port 9201)"
echo

# Verify all services
echo "🔍 Verifying services..."
echo

echo "Prometheus:        http://localhost:9090"
curl -s http://localhost:9090/-/ready && echo "  ✅ Ready" || echo "  ❌ Not ready"

echo "Grafana:           http://localhost:3000"
curl -s http://localhost:3000/api/health && echo "  ✅ Ready" || echo "  ❌ Not ready"

echo "Postgres Exporter: http://localhost:9187"
curl -s http://localhost:9187/metrics > /dev/null && echo "  ✅ Ready" || echo "  ❌ Not ready"

echo "Node Exporter:     http://localhost:9100"
curl -s http://localhost:9100/metrics > /dev/null && echo "  ✅ Ready" || echo "  ❌ Not ready"

echo "AYA Metrics:       http://localhost:9200"
curl -s http://localhost:9200/metrics > /dev/null && echo "  ✅ Ready" || echo "  ❌ Not ready"

echo "Tailscale Metrics: http://localhost:9201"
curl -s http://localhost:9201/metrics > /dev/null && echo "  ✅ Ready" || echo "  ❌ Not ready"

echo
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo
echo "Access Grafana at: http://beta.tail5f2bae.ts.net:3000"
echo "Username: arthur"
echo "Password: AyaGrafana2025!"
echo
echo "Logs:"
echo "  Docker:         docker-compose -f /Volumes/DATA/AYA/services/grafana/docker-compose-beta.yml logs -f"
echo "  AYA Metrics:    tail -f /tmp/aya_metrics_exporter.log"
echo "  Tailscale:      tail -f /tmp/tailscale_exporter.log"
echo

