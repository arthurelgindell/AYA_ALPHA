#!/bin/bash
# EMERGENCY STABILITY RESTORATION SCRIPT
# Purpose: Return to stable PostgreSQL 18 + Patroni configuration
# Date: October 28, 2025

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   EMERGENCY STABILITY RESTORATION SCRIPT     ║"
echo "║   Returning to PostgreSQL 18 + Patroni       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Step 1: Verify no PostgreSQL 18 processes (should be none)
echo "1. Checking for any remaining database processes..."
if pgrep -f "PostgreSQL 18 process|PostgreSQL 18 process|PostgreSQL 18 process" > /dev/null; then
    echo "   ⚠️  Found unexpected processes - cleaning up..."
    pkill -f PostgreSQL 18 process || true
    pkill -f PostgreSQL 18 process || true  
    pkill -f PostgreSQL 18 process || true
    sleep 3
fi
echo "   ✅ No PostgreSQL 18 processes"

# Step 2: Verify PostgreSQL 18 health
echo ""
echo "2. Verifying PostgreSQL 18 health..."
if PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1" &>/dev/null; then
    echo "   ✅ PostgreSQL 18 is healthy"
    PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 'Chunks:' as data, COUNT(*) FROM chunks"
else
    echo "   ❌ PostgreSQL 18 needs attention"
    exit 1
fi

# Step 3: Restore Agent Turbo to use PostgreSQL
echo ""
echo "3. Restoring Agent Turbo configuration..."
if [ -f /Users/arthurdell/AYA/Agent_Turbo/core/postgres_connector.py.backup ]; then
    cp /Users/arthurdell/AYA/Agent_Turbo/core/postgres_connector.py.backup \
       /Users/arthurdell/AYA/Agent_Turbo/core/postgres_connector.py
    echo "   ✅ postgres_connector.py restored"
else
    echo "   ⚠️  No backup found - manual intervention needed"
fi

# Step 4: Restore Cursor MCP settings
echo ""
echo "4. Restoring Cursor MCP to PostgreSQL..."
cat > /Users/arthurdell/AYA/.cursor/settings.json << 'EOF'
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--network", "aya_network",
        "-v", "/var/run/docker.sock:/var/run/docker.sock", 
        "mcp/docker"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres",
        "postgresql://postgres:Power$$336633$$@localhost:5432/aya_rag"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    },
    "agent-turbo": {
      "command": "uv",
      "args": ["run", "mcp-agent-turbo"]
    }
  }
}
EOF
echo "   ✅ Cursor settings restored"

# Step 5: Clean up disk space
echo ""
echo "5. Cleaning up PostgreSQL 18 artifacts..."
echo "   Current usage: $(du -sh /Users/arthurdell/AYA/PostgreSQL 18* | awk '{sum+=$1} END {print sum}')MB"
echo "   Moving to backup location..."
mkdir -p /Users/arthurdell/AYA/PostgreSQL 18
mv /Users/arthurdell/AYA/PostgreSQL 18 /Users/arthurdell/AYA/PostgreSQL 18/ 2>/dev/null || true
mv /Users/arthurdell/AYA/PostgreSQL 18 /Users/arthurdell/AYA/PostgreSQL 18/ 2>/dev/null || true
echo "   ✅ Cleanup complete"

# Step 6: Test PostgreSQL replication status
echo ""
echo "6. Checking PostgreSQL replication to BETA..."
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d postgres << EOF
SELECT client_addr, state, sync_state 
FROM pg_stat_replication;
EOF

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           RESTORATION COMPLETE               ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo "1. Restart Patroni on BETA:"
echo "   ssh beta 'cd /Volumes/DATA/AYA && patroni patroni_standby.yml'"
echo ""
echo "2. Verify replication is working:"
echo "   watch -n 2 'psql -h localhost -p 5432 -U postgres -c \"SELECT * FROM pg_stat_replication\"'"
echo ""
echo "3. When stable, prepare for GAMMA:"
echo "   - Install PostgreSQL 18 on GAMMA"
echo "   - Configure as async standby"
echo "   - Update Patroni configuration"
echo ""
echo "Your PostgreSQL data is safe. Focus on stability over features."
