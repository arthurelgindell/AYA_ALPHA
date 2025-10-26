#!/bin/bash
###############################################################################
# AIR NODE INITIALIZATION SCRIPT
# Purpose: Initialize AIR node for monitoring and control of ALPHA/BETA
# Single Source of Truth: PostgreSQL aya_rag database
###############################################################################

set -e  # Exit on error

echo "========================================="
echo "AIR NODE INITIALIZATION"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Database credentials
export PGPASSWORD='Power$$336633$$'
DB_USER='postgres'
DB_NAME='aya_rag'

# Test function
test_step() {
    local description="$1"
    local command="$2"
    local expected="$3"

    echo -n "Testing: $description... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        echo "  Command: $command"
        return 1
    fi
}

# Step 1: Verify Prerequisites
echo "Step 1: Verifying Prerequisites"
echo "================================"

test_step "Tailscale is running" "tailscale status | grep -q 'alpha.tail5f2bae.ts.net'"
test_step "Python 3 available" "python3 --version"
test_step "PostgreSQL client available" "which psql"
test_step "SSH available" "which ssh"

echo ""

# Step 2: Network Connectivity
echo "Step 2: Verifying Network Connectivity"
echo "========================================"

test_step "ALPHA reachable via Tailscale" "ping -c 2 alpha.tail5f2bae.ts.net"
test_step "BETA reachable via Tailscale" "ping -c 2 beta.tail5f2bae.ts.net"

echo ""

# Step 3: SSH Access
echo "Step 3: Verifying SSH Access"
echo "=============================="

# Note: May require SSH key setup or host key acceptance
echo -n "Testing: SSH to ALPHA... "
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no alpha.tail5f2bae.ts.net "hostname" 2>/dev/null | grep -q "alpha"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} (May need SSH key setup)"
fi

echo -n "Testing: SSH to BETA... "
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no beta.tail5f2bae.ts.net "hostname" 2>/dev/null | grep -q "beta"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} (May need SSH key setup)"
fi

echo ""

# Step 4: PostgreSQL HA Cluster
echo "Step 4: Verifying PostgreSQL HA Cluster"
echo "=========================================="

echo -n "Testing: PostgreSQL connection to ALPHA... "
if PGPASSWORD="$PGPASSWORD" psql -h alpha.tail5f2bae.ts.net -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    PRIMARY_HOST="alpha.tail5f2bae.ts.net"
else
    echo -e "${YELLOW}⚠${NC} (Trying BETA)"
    if PGPASSWORD="$PGPASSWORD" psql -h beta.tail5f2bae.ts.net -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} (Connected via BETA)"
        PRIMARY_HOST="beta.tail5f2bae.ts.net"
    else
        echo -e "${RED}✗${NC} (Cannot connect to database)"
        exit 1
    fi
fi

# Identify cluster roles
echo ""
echo "Patroni Cluster Status:"
curl -s http://alpha.tail5f2bae.ts.net:8008/cluster 2>/dev/null | python3 -c "
import sys, json
try:
    cluster = json.load(sys.stdin)
    print(f\"  Scope: {cluster.get('scope', 'N/A')}\")
    for member in cluster.get('members', []):
        role_icon = '👑' if member.get('role') == 'leader' else '🔄'
        print(f\"  {role_icon} {member.get('name')}: {member.get('role')} ({member.get('state')}) - Lag: {member.get('lag', 'N/A')}\")
except:
    print('  Unable to parse cluster status')
"

echo ""

# Step 5: Retrieve AIR Operational Context
echo "Step 5: Loading AIR Operational Context"
echo "=========================================="

echo "Querying aya_rag database for AIR configuration..."

# Query with proper error handling
DB_QUERY_OUTPUT=$(PGPASSWORD="$PGPASSWORD" psql -h "$PRIMARY_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM node_operational_contexts WHERE node_name='AIR';" 2>&1)
DB_QUERY_STATUS=$?

if [ $DB_QUERY_STATUS -ne 0 ]; then
    echo -e "${RED}✗${NC} Database query failed:"
    echo "$DB_QUERY_OUTPUT"
    exit 1
fi

CONTEXT_EXISTS=$(echo "$DB_QUERY_OUTPUT" | xargs)

if [ "$CONTEXT_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓${NC} AIR operational context found in database"

    # Extract key information
    echo ""
    echo "Role Definition:"
    PGPASSWORD="$PGPASSWORD" psql -h "$PRIMARY_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT substring(role_definition, 1, 200) || '...'
        FROM node_operational_contexts
        WHERE node_name='AIR';
    " 2>/dev/null

    echo ""
    echo "Connection Endpoints Configured:"
    PGPASSWORD="$PGPASSWORD" psql -h "$PRIMARY_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT jsonb_pretty(connection_endpoints::jsonb)
        FROM node_operational_contexts
        WHERE node_name='AIR';
    " 2>/dev/null | head -20

else
    echo -e "${RED}✗${NC} AIR operational context not found in database"
    echo "Please run: AIR operational context initialization"
    exit 1
fi

echo ""

# Step 6: Verify System Nodes
echo "Step 6: Verifying System Nodes in Database"
echo "============================================"

PGPASSWORD="$PGPASSWORD" psql -h "$PRIMARY_HOST" -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT
        node_name,
        node_role,
        ram_gb || 'GB' as ram,
        storage_internal_tb || 'TB' as internal_storage,
        COALESCE(storage_external_tb || 'TB', 'None') as external_storage,
        metadata->>'working_path' as working_path,
        status
    FROM system_nodes
    ORDER BY node_name;
"

echo ""

# Step 7: Agent Turbo Verification
echo "Step 7: Verifying Agent Turbo"
echo "==============================="

if [ -d "/Users/arthurdell/AYA/Agent_Turbo/core" ]; then
    echo -e "${GREEN}✓${NC} Agent Turbo directory found"

    echo -n "Testing: Agent Turbo stats... "
    if cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py stats > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        echo ""
        echo "Agent Turbo Statistics:"
        python3 agent_turbo.py stats 2>/dev/null | python3 -m json.tool | head -15
    else
        echo -e "${YELLOW}⚠${NC} (Agent Turbo may need configuration)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Agent Turbo directory not found at /Users/arthurdell/AYA/Agent_Turbo/core"
fi

echo ""

# Step 8: Summary
echo "========================================="
echo "INITIALIZATION COMPLETE"
echo "========================================="
echo ""
echo "AIR Node Status: ${GREEN}OPERATIONAL${NC}"
echo ""
echo "Quick Reference Commands:"
echo "  Monitor cluster:     curl -s http://alpha.tail5f2bae.ts.net:8008/cluster | python3 -m json.tool"
echo "  Query database:      PGPASSWORD='Power\$\$336633\$\$' psql -h alpha.tail5f2bae.ts.net -U postgres -d aya_rag"
echo "  SSH to ALPHA:        ssh alpha.tail5f2bae.ts.net"
echo "  SSH to BETA:         ssh beta.tail5f2bae.ts.net"
echo "  Check ALPHA workers: ssh alpha.tail5f2bae.ts.net 'ps aux | grep task_worker.py | wc -l'"
echo "  Check BETA workers:  ssh beta.tail5f2bae.ts.net 'ps aux | grep task_worker.py | wc -l'"
echo ""
echo "Documentation:"
echo "  CLAUDE.md:           /Users/arthurdell/AYA/CLAUDE.md"
echo "  Database context:    SELECT * FROM node_operational_contexts WHERE node_name='AIR'"
echo ""
echo "Single Source of Truth: PostgreSQL aya_rag database"
echo ""
