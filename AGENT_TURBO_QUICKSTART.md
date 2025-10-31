# Agent Turbo Quick Start Guide

**Purpose**: Zero-token initialization for any AI agent working with the AYA platform.

**Last Updated**: October 29, 2025
**Database**: PostgreSQL 18 (production database)
**Status**: ✅ PRODUCTION READY

---

## One-Command Initialization

```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py verify
```

**Expected output**: `✅ AGENT_TURBO: VERIFIED AND OPERATIONAL`

**Time**: ~3 seconds on cold start, <1 second on warm start

---

## What Gets Verified

1. **PostgreSQL 18 Connection** - Production database on port 5432
2. **MLX GPU Acceleration** - 80 GPU cores (M3 Ultra)
3. **Knowledge Base** - 124+ entries with pgvector embeddings
4. **RAM Disk Cache** - 5 cache directories ready
5. **LM Studio** - Local LLM inference (optional)
6. **Data Persistence** - Write/read cycle to database

---

## Pre-Flight Checklist

### Database Prerequisites

✅ **PostgreSQL 18 must be running** (port 5432):
```bash
# Check PostgreSQL processes
ps aux | grep postgres | grep -v grep

# Expected: PostgreSQL processes visible
```

✅ **Database exists**:
```bash
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT version();"

# Expected: PostgreSQL 18.x
```

---

## Common Issues and Fixes

### Issue 1: "PostgreSQL connection failed"

**Symptom**: Verification fails at database connection step

**Diagnosis**:
```bash
# Test PostgreSQL connectivity
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1;"
```

**Fix 1 - PostgreSQL not running**:
```bash
# Check if PostgreSQL is running
ps aux | grep postgres | grep -v grep

# If not running, check Patroni status
curl http://localhost:8008/patroni
```

**Fix 2 - Database connection issues**:
```bash
# Verify PostgreSQL is accessible
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT version();"
```

**Fix 3 - Code bug (fixed October 28, 2025)**:
- **Bug**: `fetch=True` (boolean) instead of `fetch='all'` (string)
- **Status**: Fixed in agent_turbo.py (7 instances corrected)
- **Verification**: Search for `fetch=True` in agent_turbo.py should return 0 results

---

### Issue 2: "Data not persisted in PostgreSQL"

**Symptom**: Connection works but write operations fail

**Diagnosis**:
```bash
# Check if agent_knowledge table exists
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18/postgres/bin/psql \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag \
  -c "SELECT COUNT(*) FROM agent_knowledge;"
```

**Fix - Table doesn't exist**:
```bash
# Apply schema migration
PGPASSWORD='Power$$336633$$' /Users/arthurdell/AYA/PostgreSQL 18/postgres/bin/psql \
  -h 127.0.0.1 -p 5432 -U PostgreSQL 18 -d aya_rag \
  -f /Users/arthurdell/AYA/aya_schema_implementation.sql
```

---

### Issue 3: MLX GPU Acceleration Not Available

**Symptom**: `using_gpu: false` in stats output

**Diagnosis**:
```bash
# Check MLX installation
python3 -c "import mlx.core as mx; print(mx.default_device())"

# Expected: Device(gpu, 0)
```

**Fix - MLX not installed**:
```bash
# Install MLX for Apple Silicon
pip3 install mlx==0.29.1
```

---

## Basic Operations Reference

### 1. Verify System
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_turbo.py verify
```

### 2. Get Statistics
```bash
python3 agent_turbo.py stats 2>&1 | grep -v "Warning:" | python3 -m json.tool
```

**Key Metrics**:
- `knowledge_entries` - Total knowledge base entries
- `embedding_coverage` - Percentage with vector embeddings
- `using_gpu` - GPU acceleration active (should be true)
- `gpu_cores` - Available GPU cores (should be 80)

### 3. Query Knowledge Base
```bash
python3 agent_turbo.py query "your search query"
```

**Returns**: Top 5 semantic search results with similarity scores

### 4. Add Knowledge Entry
```bash
python3 agent_turbo.py add "your knowledge content"
```

**Creates**: Entry with SHA256 hash, MLX embedding, and pgvector storage

---

## Performance Benchmarks

| Operation | Target | Actual (October 28, 2025) |
|-----------|--------|---------------------------|
| Knowledge Add | <50ms | 27.9ms |
| Knowledge Query | <100ms | 2.9ms |
| Landing Context | <100ms | 27.4ms |
| Session Creation | <20ms | 12.9ms |
| Verification (cold) | <5s | 3.2s |
| Verification (warm) | <1s | 0.8s |

---

## PostgreSQL 18 Architecture

**Deployment**: PostgreSQL 18 single-node
**Host**: localhost (127.0.0.1)
**Ports**:
- 5432 - PostgreSQL wire protocol

**Connection Configuration**:
```python
{
    'host': 'localhost',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': 'Power$$336633$$'
}
```

---

## Health Check Script

Save this as `/Users/arthurdell/AYA/Agent_Turbo/scripts/health_check.sh`:

```bash
#!/bin/bash
# Agent Turbo Health Check
# Usage: ./health_check.sh

echo "=== Agent Turbo Health Check ==="
echo ""

# 1. Check PostgreSQL 18
echo "1. PostgreSQL 18 Status:"
if ps aux | grep postgres | grep -v grep > /dev/null; then
    echo "   ✅ PostgreSQL 18 processes running"
else
    echo "   ❌ PostgreSQL 18 NOT running"
    exit 1
fi

# 2. Check Database Connectivity
echo "2. Database Connectivity:"
if PGPASSWORD='Power$$336633$$' psql \
   -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ Database reachable"
else
    echo "   ❌ Database connection FAILED"
    exit 1
fi

# 3. Check Agent Turbo Tables
echo "3. Agent Turbo Schema:"
TABLE_COUNT=$(PGPASSWORD='Power$$336633$$' psql \
   -h localhost -p 5432 -U postgres -d aya_rag -t -c \
   "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'agent_%';")
if [ "$TABLE_COUNT" -eq 7 ]; then
    echo "   ✅ All 7 Agent Turbo tables present"
else
    echo "   ❌ Expected 7 tables, found: $TABLE_COUNT"
    exit 1
fi

# 4. Check MLX GPU
echo "4. MLX GPU Acceleration:"
if python3 -c "import mlx.core as mx; print(mx.default_device())" 2>&1 | grep -q "gpu"; then
    echo "   ✅ MLX GPU available"
else
    echo "   ⚠️  MLX GPU not available (will use CPU)"
fi

# 5. Run Agent Turbo Verification
echo "5. Agent Turbo Verification:"
cd /Users/arthurdell/AYA/Agent_Turbo/core
if python3 agent_turbo.py verify 2>&1 | grep -q "VERIFIED AND OPERATIONAL"; then
    echo "   ✅ Agent Turbo OPERATIONAL"
else
    echo "   ❌ Agent Turbo verification FAILED"
    exit 1
fi

echo ""
echo "=== All Systems Operational ==="
```

Make executable:
```bash
chmod +x /Users/arthurdell/AYA/Agent_Turbo/scripts/health_check.sh
```

---

## Database Configuration

**Current**: PostgreSQL 18 (production)
- Port: 5432
- Database: `aya_rag`
- User: `postgres`
- Binary: Standard PostgreSQL 18 installation

---

## Troubleshooting Decision Tree

```
Is verification failing?
├─ Yes → Check PostgreSQL 18 running (ps aux | grep postgres)
│   ├─ Not running → Check Patroni status (curl http://localhost:8008/patroni)
│   └─ Running → Check database connectivity
│       ├─ Test: psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1;"
│       └─ If fails → Check Patroni cluster status
└─ No → System operational ✅
```

---

## For Future AI Agents

**If you're reading this as a new agent working on AYA**:

1. **Start here**: Run `python3 agent_turbo.py verify` from Agent_Turbo/core/
2. **If it works**: You're done! System is operational.
3. **If it fails**: Follow "Common Issues" section above
4. **Don't debug blindly**: Use health_check.sh script first
5. **Report new issues**: Add to this document if you discover new failure modes

**Expected token usage for initialization**: <500 tokens (just reading this file)

---

## Document Maintenance

**This document must be updated when**:
- PostgreSQL 18 configuration changes
- New failure modes are discovered
- Performance benchmarks drift by >20%
- Database schema migrations occur

**Update procedure**: Edit this file, test all commands, verify zero-token initialization still works.

---

**Document Status**: ✅ VERIFIED
**Last Verification**: October 29, 2025 (ALPHA)
**Next Review**: When database configuration changes
