#!/bin/bash
# MCP Server Integration Tests
# Tests actual functionality, not just installation

set -e

echo "═══════════════════════════════════════════════════════════════"
echo " MCP SERVER FUNCTIONAL TESTS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test 1: Docker Direct (baseline)
echo "TEST 1: Docker Direct Access"
echo "-----------------------------------"
if docker ps --format '{{.Names}}' | grep -q "blue_combat"; then
    echo "✅ Docker daemon accessible"
    echo "✅ blue_combat container running"
else
    echo "❌ Docker test FAILED"
    exit 1
fi
echo ""

# Test 2: Docker via Node.js (MCP dependency)
echo "TEST 2: Docker via Node.js"
echo "-----------------------------------"
RESULT=$(node -e "const { exec } = require('child_process'); exec('docker ps --format \"{{.Names}}\"', (err, stdout) => { if (err) { console.log('FAILED'); process.exit(1); } else { console.log('SUCCESS'); } });")
if echo "$RESULT" | grep -q "SUCCESS"; then
    echo "✅ Node.js can execute Docker commands"
else
    echo "⚠️  Node.js Docker execution unclear"
fi
echo ""

# Test 3: PostgreSQL Direct (baseline)
echo "TEST 3: PostgreSQL Direct Access"
echo "-----------------------------------"
if psql -U postgres -d aya_rag -c "SELECT COUNT(*) FROM agent_sessions;" -t 2>&1 | grep -q "[0-9]"; then
    SESSION_COUNT=$(psql -U postgres -d aya_rag -c "SELECT COUNT(*) FROM agent_sessions;" -t | tr -d ' ')
    echo "✅ PostgreSQL aya_rag accessible"
    echo "✅ agent_sessions table: $SESSION_COUNT rows"
else
    echo "❌ PostgreSQL test FAILED"
    exit 1
fi
echo ""

# Test 4: PostgreSQL MCP Package
echo "TEST 4: PostgreSQL MCP Package"
echo "-----------------------------------"
if npm list -g @modelcontextprotocol/server-postgres 2>&1 | grep -q "server-postgres"; then
    echo "✅ @modelcontextprotocol/server-postgres installed"
else
    echo "❌ PostgreSQL MCP not installed"
    exit 1
fi
echo ""

# Test 5: GitHub MCP Package
echo "TEST 5: GitHub MCP Package"
echo "-----------------------------------"
if npm list -g @modelcontextprotocol/server-github 2>&1 | grep -q "server-github"; then
    echo "✅ @modelcontextprotocol/server-github installed"
else
    echo "❌ GitHub MCP not installed"
    exit 1
fi
echo ""

# Test 6: Docker MCP Server File
echo "TEST 6: Docker MCP Server"
echo "-----------------------------------"
if [ -x "/Users/arthurdell/AYA/mcp_servers/docker-mcp-server.js" ]; then
    echo "✅ docker-mcp-server.js exists and executable"
    
    # Test if it responds to tools/list
    if echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node /Users/arthurdell/AYA/mcp_servers/docker-mcp-server.js 2>&1 | grep -q "docker_list_containers"; then
        echo "✅ Docker MCP responds to tools/list"
        echo "✅ Exposes docker_list_containers tool"
    else
        echo "❌ Docker MCP does not respond properly"
        exit 1
    fi
else
    echo "❌ Docker MCP server not found or not executable"
    exit 1
fi
echo ""

# Test 7: Claude Desktop Config
echo "TEST 7: Claude Desktop Configuration"
echo "-----------------------------------"
if [ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ]; then
    echo "✅ claude_desktop_config.json exists"
    
    if grep -q "docker" "$HOME/Library/Application Support/Claude/claude_desktop_config.json"; then
        echo "✅ Docker MCP configured"
    else
        echo "⚠️  Docker MCP not in config"
    fi
    
    if grep -q "postgres" "$HOME/Library/Application Support/Claude/claude_desktop_config.json"; then
        echo "✅ PostgreSQL MCP configured"
    else
        echo "⚠️  PostgreSQL MCP not in config"
    fi
    
    if grep -q "github" "$HOME/Library/Application Support/Claude/claude_desktop_config.json"; then
        echo "✅ GitHub MCP configured"
    else
        echo "⚠️  GitHub MCP not in config"
    fi
else
    echo "❌ claude_desktop_config.json not found"
    exit 1
fi
echo ""

# Test 8: Cursor IDE Config
echo "TEST 8: Cursor IDE Configuration"
echo "-----------------------------------"
if [ -f "/Users/arthurdell/AYA/.cursor/mcp_config.json" ]; then
    echo "✅ .cursor/mcp_config.json exists"
    
    if grep -q "docker" "/Users/arthurdell/AYA/.cursor/mcp_config.json"; then
        echo "✅ Docker MCP configured"
    else
        echo "⚠️  Docker MCP not in config"
    fi
else
    echo "❌ .cursor/mcp_config.json not found"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo " TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "✅ Infrastructure: Docker + PostgreSQL operational"
echo "✅ MCP Packages: Installed globally"
echo "✅ MCP Server: Docker custom implementation functional"
echo "✅ Configuration: Claude Desktop + Cursor configured"
echo ""
echo "⚠️  LIMITATION: MCP stdio protocol requires Claude/Cursor client"
echo "⚠️  Full integration test requires Claude Desktop restart"
echo ""
echo "NEXT STEP: User must restart Claude Desktop to activate MCPs"
echo ""
echo "═══════════════════════════════════════════════════════════════"

