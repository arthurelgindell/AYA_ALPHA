#!/bin/bash
"""
GLADIATOR SSH Tunnel Setup
Creates bidirectional tunnels for LM Studio cross-system access
"""

echo "🔗 Setting up SSH tunnels for GLADIATOR combat..."

# Kill existing tunnels
echo "🧹 Cleaning up existing tunnels..."
pkill -f "ssh.*1234.*1235" 2>/dev/null || true
ssh beta.local "pkill -f 'ssh.*1234.*1235'" 2>/dev/null || true

# Create ALPHA → BETA tunnel (ALPHA can access BETA's LM Studio via localhost:1235)
echo "🔴 Creating ALPHA → BETA tunnel (Red Team access)..."
ssh -L 1235:localhost:1234 beta.local -N -f

# Create BETA → ALPHA tunnel (BETA can access ALPHA's LM Studio via localhost:1235)  
echo "🔵 Creating BETA → ALPHA tunnel (Blue Team access)..."
ssh beta.local "ssh -L 1235:localhost:1234 alpha.local -N -f"

# Verify tunnels
echo "✅ Verifying tunnels..."
sleep 2

echo "🔴 Testing ALPHA → BETA tunnel..."
curl -s http://localhost:1235/v1/models 2>&1 | head -3

echo "🔵 Testing BETA → ALPHA tunnel..."
ssh beta.local "curl -s http://localhost:1235/v1/models 2>&1 | head -3"

echo ""
echo "🎯 SSH tunnels established!"
echo "   ALPHA accesses BETA LM Studio: http://localhost:1235"
echo "   BETA accesses ALPHA LM Studio: http://localhost:1235"
echo ""
echo "Ready for combat deployment!"
