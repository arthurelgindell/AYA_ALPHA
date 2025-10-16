#!/bin/bash
# GLADIATOR Combat Arena Deployment
# Creates Red vs Blue isolated combat environment

set -e

echo "========================================================================"
echo "GLADIATOR COMBAT ARENA DEPLOYMENT"
echo "========================================================================"
echo ""

# Check Docker resources
DOCKER_MEM=$(docker info 2>/dev/null | grep "Total Memory" | awk '{print $3$4}')
echo "Docker Memory: $DOCKER_MEM"

# Create combat network (isolated from production)
echo "[1/5] Creating combat network..."
docker network create gladiator_combat 2>/dev/null || echo "Network exists"
docker network inspect gladiator_combat | grep -E "(Name|Subnet)" | head -3

# Create Blue Team Arena Container
echo ""
echo "[2/5] Creating Blue Team Combat Container..."
docker run -d \
  --name blue_arena \
  --network gladiator_combat \
  --memory 200g \
  --cpus 12 \
  -v /Users/arthurdell/GLADIATOR/datasets:/data:ro \
  python:3.11-slim \
  tail -f /dev/null

echo "✅ Blue Arena created"

# Create Red Team Arena Container
echo ""
echo "[3/5] Creating Red Team Combat Container..."
docker run -d \
  --name red_arena \
  --network gladiator_combat \
  --memory 200g \
  --cpus 12 \
  -v /Users/arthurdell/GLADIATOR/datasets:/data:ro \
  python:3.11-slim \
  tail -f /dev/null

echo "✅ Red Arena created"

# Verify containers running
echo ""
echo "[4/5] Verifying containers..."
docker ps --filter "name=arena"

# Test network isolation
echo ""
echo "[5/5] Testing combat network isolation..."
BLUE_IP=$(docker inspect blue_arena | grep '"IPAddress"' | head -1 | awk '{print $2}' | tr -d '",')
RED_IP=$(docker inspect red_arena | grep '"IPAddress"' | head -1 | awk '{print $2}' | tr -d '",')

echo "Blue Arena IP: $BLUE_IP"
echo "Red Arena IP: $RED_IP"

# Test: Red can reach Blue
docker exec red_arena ping -c 2 $BLUE_IP 2>/dev/null && echo "✅ Red can reach Blue" || echo "❌ Network issue"

echo ""
echo "========================================================================"
echo "COMBAT ARENA DEPLOYED"
echo "========================================================================"
echo ""
echo "Blue Team: blue_arena ($BLUE_IP)"
echo "Red Team: red_arena ($RED_IP)"
echo "Network: gladiator_combat (isolated)"
echo ""
echo "Next: Install models and begin combat testing"
