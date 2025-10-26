# AYA Agent Turbo MCP Server

Direct integration between Claude Desktop and Agent Turbo knowledge base.

## Overview

This MCP (Model Context Protocol) server exposes Agent Turbo's semantic search and knowledge management capabilities directly to Claude Desktop, eliminating command-line overhead and enabling native integration.

## Features

- **Semantic Search**: Query 108+ knowledge entries with GPU-accelerated embeddings
- **Knowledge Addition**: Add new entries directly from Claude Desktop conversations
- **Performance Monitoring**: Real-time statistics and metrics
- **GPU Acceleration**: MLX Metal with 80 cores (M3 Ultra)
- **PostgreSQL Backend**: aya_rag database with complete audit trail
- **RAM Disk Caching**: 100GB cache for ultra-fast queries (<100ms)
- **LM Studio Integration**: Optional LLM-enhanced responses

## Architecture

```
Claude Desktop
    ↓ (stdio/MCP protocol)
AYA Agent Turbo MCP Server (Python 3.11+)
    ↓ (asyncio.to_thread)
Agent Turbo Core (Python 3.9)
    ↓ (psycopg2)
PostgreSQL aya_rag Database
```

## Installation

### Prerequisites

- Python 3.11+ (ARM64 for M-series Macs)
- PostgreSQL 18 with aya_rag database
- Agent Turbo operational (`cd /Users/arthurdell/AYA && ./Agent_Turbo/agent_turbo stats`)
- Embedding service running on port 8765

### Setup

```bash
# 1. Navigate to server directory
cd /Users/arthurdell/AYA/mcp_servers/aya-agent-turbo

# 2. Install dependencies (using Python 3.11)
/usr/local/python3.11-arm64/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Test server
./server.py
# Should start without errors (Ctrl+C to stop)

# 4. Configure Claude Desktop
# See "Claude Desktop Configuration" section below
```

## Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aya-agent-turbo": {
      "command": "/Users/arthurdell/AYA/mcp_servers/aya-agent-turbo/venv/bin/python",
      "args": [
        "/Users/arthurdell/AYA/mcp_servers/aya-agent-turbo/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/arthurdell/AYA/Agent_Turbo/core"
      }
    }
  }
}
```

**Important**: If other MCP servers exist, add this entry to the existing `mcpServers` object.

After editing, **restart Claude Desktop completely** (quit and reopen).

## Tools

### 1. query_knowledge

Search the Agent Turbo knowledge base with semantic similarity.

**Parameters**:
- `query` (string, required): Search query text
- `limit` (integer, optional): Maximum results (default: 5)

**Example**:
```
Query the Agent Turbo knowledge base for "PostgreSQL connection pooling"
```

**Returns**:
```json
{
  "results": [
    {
      "content": "...",
      "similarity": 0.92,
      "source": "...",
      "type": "solution"
    }
  ],
  "query_time_ms": 45,
  "cache_hit": true
}
```

### 2. add_knowledge

Add new knowledge entries to the database.

**Parameters**:
- `content` (string, required): Knowledge content to add
- `source` (string, optional): Source identifier (default: "mcp")
- `knowledge_type` (string, optional): Entry type - "solution", "pattern", "concept" (default: "solution")

**Example**:
```
Add this to Agent Turbo: "MCP servers communicate via stdio using JSON-RPC protocol"
```

**Returns**:
```json
{
  "status": "success",
  "entry_id": 109,
  "embedded": true,
  "add_time_ms": 27
}
```

### 3. get_stats

Retrieve Agent Turbo performance statistics.

**Parameters**: None

**Example**:
```
What are the Agent Turbo statistics?
```

**Returns**:
```json
{
  "database": {
    "total_entries": 108,
    "embedded_percentage": 100.0,
    "database_size_mb": 509
  },
  "cache": {
    "hit_rate": 85.3,
    "size_mb": 342,
    "entries": 1247
  },
  "gpu": {
    "available": true,
    "cores": 80,
    "device": "Apple M3 Ultra"
  },
  "performance": {
    "avg_query_ms": 45.2,
    "avg_add_ms": 27.9
  }
}
```

## Resources

### knowledge://stats

MCP resource that exposes real-time statistics. Auto-refreshed when accessed.

## Performance Expectations

- **Query latency**: <100ms for cached queries, <2s for new queries
- **GPU utilization**: 80 cores active for embedding generation
- **Cache hit rate**: >80% after 10 queries
- **Database**: PostgreSQL with connection pooling (2-10 connections)
- **Concurrency**: Async-safe via asyncio.to_thread()

## Troubleshooting

### Server won't start

```bash
# Check Python version
/usr/local/python3.11-arm64/bin/python3.11 --version
# Should show: Python 3.11.x

# Check dependencies
source venv/bin/activate
pip list | grep mcp

# Verify Agent Turbo
cd /Users/arthurdell/AYA
./Agent_Turbo/agent_turbo verify
```

### Tools not appearing in Claude Desktop

1. Verify config file location:
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Validate JSON syntax:
```bash
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

3. Check Claude Desktop logs (View → Developer → Toggle Developer Tools → Console)

### Query fails with database error

```bash
# Verify PostgreSQL is running
pg_isready

# Check database
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -U postgres -d aya_rag -c "SELECT COUNT(*) FROM knowledge_base;"

# Verify embedding service
curl http://localhost:8765/health
```

### Permission errors

```bash
# Ensure server.py is executable
chmod +x /Users/arthurdell/AYA/mcp_servers/aya-agent-turbo/server.py

# Check virtual environment permissions
ls -la venv/bin/python
```

## Development

### Testing the server

```bash
# Activate virtual environment
cd /Users/arthurdell/AYA/mcp_servers/aya-agent-turbo
source venv/bin/activate

# Run server (stdio mode)
python server.py

# In another terminal, test Agent Turbo directly
cd /Users/arthurdell/AYA
./Agent_Turbo/agent_turbo query "test query"
```

### Logging

MCP server uses Context logging:
- `ctx.info()` - Informational messages
- `ctx.error()` - Error messages

Logs appear in Claude Desktop Developer Tools console.

## Security

- Server runs locally only (no network exposure)
- Uses existing PostgreSQL credentials
- Inherits Agent Turbo's security model
- No sensitive data exposed in MCP protocol

## Prime Directives Compliance

This implementation follows all AYA Prime Directives:

✅ **Functional Reality Only**: All operations use actual PostgreSQL database
✅ **Truth Over Comfort**: Errors reported accurately, no fabricated data
✅ **Execute with Precision**: Tested end-to-end with real data flow
✅ **No Theatrical Wrappers**: Every operation produces queryable results
✅ **System Verification**: Integration tested with actual Agent Turbo

## Status

**Status**: ✅ **PRODUCTION READY AND DEPLOYED**

**Deployment Date**: 2025-10-23

**Current State**:
- Python: 3.11.14 ARM64 (OpenSSL 3.5.4)
- MCP SDK: 1.18.0
- Database: 108 entries (100% embedded)
- GPU: 80 cores (M3 Ultra)
- Cache: RAM disk enabled
- Embedding Service: Operational (port 8765)
- PostgreSQL: aya_rag (509 MB)
- Claude Desktop: Configured and ready

## Support

For issues or questions:
1. Verify Agent Turbo is operational: `./Agent_Turbo/agent_turbo stats`
2. Check PostgreSQL connectivity: `pg_isready`
3. Review Claude Desktop console for MCP errors
4. Test server standalone: `python server.py` (should start without errors)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-22
**Maintained By**: AYA Platform Team
