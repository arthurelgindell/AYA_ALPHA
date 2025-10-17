# AGENT TURBO - ALPHA DEPLOYMENT GUIDE
**Package**: AT_Beta → Agent_Turbo (on Alpha)  
**Target Location**: `/Users/arthurdell/AYA/Agent_Turbo`  
**Deployment Date**: 2025-10-11  

---

## DEPLOYMENT STEPS

### 1. Transfer Package to ALPHA

Copy this entire `AT_Beta` folder to ALPHA and rename it:

```bash
# On ALPHA
mkdir -p /Users/arthurdell/AYA
# ... transfer AT_Beta folder ...
mv AT_Beta /Users/arthurdell/AYA/Agent_Turbo
cd /Users/arthurdell/AYA/Agent_Turbo
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Or install individually:
pip3 install mlx mlx-nn psutil requests psycopg2-binary
```

### 3. Verify System Configuration

```bash
# Check Python version (needs 3.9+)
python3 --version

# Verify LM Studio is running
curl http://localhost:1234/v1/models

# Check if Apple Silicon (for GPU acceleration)
system_profiler SPHardwareDataType | grep "Chip:"
```

### 4. Configure for ALPHA

The `config/alpha_config.py` file is already configured for ALPHA:
- ALPHA_IP: 100.106.170.128
- BETA_IP: 100.84.202.68
- System Role: PRIMARY
- PostgreSQL: localhost (ALPHA is primary)

**Verify settings match your setup:**
```bash
cat config/alpha_config.py
```

### 5. Run Verification

```bash
# Test Agent Turbo functionality
python3 core/agent_turbo.py verify
```

Expected output:
```
🚀 Initializing AGENT_TURBO Mode...
✅ MLX GPU acceleration enabled (XX cores)
🚀 GPU optimizer initialized: XX cores
🚀 LM Studio client initialized
✅ AGENT_TURBO Mode ready!
✅ AGENT_TURBO: VERIFIED AND OPERATIONAL
```

### 6. Get System Statistics

```bash
# Check Agent Turbo stats
python3 core/agent_turbo.py stats
```

This will show:
- Knowledge base entries
- Memory usage
- GPU statistics (if Apple Silicon)
- LM Studio connection status
- Cache performance metrics

### 7. Optional: Create RAM Disk (Performance Boost)

If you want ultra-fast cache performance:

```bash
# Create RAM disk at /Volumes/DATA/Agent_RAM
# (Instructions depend on your system setup)
```

Agent Turbo will automatically use it if available, otherwise falls back to `~/.agent_turbo/agent_turbo_cache`

---

## VERIFICATION CHECKLIST

- [ ] Python 3.9+ installed
- [ ] All dependencies installed (mlx, psutil, requests, psycopg2-binary)
- [ ] LM Studio running on localhost:1234
- [ ] PostgreSQL aya_rag database accessible
- [ ] Agent Turbo verification passed
- [ ] GPU acceleration enabled (if Apple Silicon)
- [ ] LM Studio client connected

---

## ARCHITECTURE

```
ALPHA (Primary):
├── Agent Turbo → Local SQLite cache (~/.agent_turbo/agent_turbo.db)
│   ├── Purpose: Performance enhancement
│   ├── GPU: MLX acceleration (if Apple Silicon)
│   └── Cache: RAM disk or fallback to home directory
│
├── LM Studio → Local model inference (localhost:1234)
│
└── PostgreSQL aya_rag → PRIMARY database (localhost:5432)
    └── Single source of truth ✅

BETA (Replica):
├── Agent Turbo → Local SQLite cache (independent)
├── LM Studio → Local model inference
└── PostgreSQL aya_rag → READ-ONLY replica
```

**Key Design Principles:**
- PostgreSQL = Single source of truth (primary on ALPHA, replica on BETA)
- Agent Turbo = Performance cache (independent on each system)
- Each system optimizes for local LM Studio (no network latency)

---

## DATABASE PATHS

- **Agent Turbo Cache**: `~/.agent_turbo/agent_turbo.db` (SQLite, local)
- **PostgreSQL**: `localhost:5432/aya_rag` (Primary on ALPHA)
- **RAM Disk Cache**: `/Volumes/DATA/Agent_RAM/cache` (optional)

---

## TROUBLESHOOTING

### No GPU Acceleration

```bash
# Check if MLX is installed
python3 -c "import mlx.core as mx; print(mx.metal.is_available())"

# If False, you may be on Intel/x86 (MLX requires Apple Silicon)
# Agent Turbo will work in CPU mode
```

### LM Studio Connection Failed

```bash
# Check LM Studio is running
curl http://localhost:1234/v1/models

# If different port, update config/alpha_config.py:
# LM_STUDIO_URL = "http://localhost:YOUR_PORT/v1"
```

### PostgreSQL Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d aya_rag -c "SELECT current_database();"

# Verify credentials in config/alpha_config.py
```

---

## PERFORMANCE EXPECTATIONS

### With Apple Silicon (M1/M2/M3/M4):
- ✅ GPU acceleration: <100ms cached queries
- ✅ 80%+ token reduction on repeated operations
- ✅ 50%+ cache hit rate after 10 queries

### Intel/x86 (CPU mode):
- ⚠️ No GPU acceleration
- ✅ Still functional, slower performance
- ✅ Cache system still active

---

## TESTING AGENT TURBO

```bash
# Add knowledge
python3 core/agent_turbo.py add "Test knowledge entry from ALPHA"

# Query knowledge
python3 core/agent_turbo.py query "Test"

# Check statistics
python3 core/agent_turbo.py stats
```

---

## NEXT STEPS

1. Run verification script: `scripts/verify_cursor_integration.py`
2. Benchmark performance: `scripts/performance_benchmark.py`
3. Test LM Studio integration
4. Verify PostgreSQL coordination with BETA
5. Compare ALPHA vs BETA performance metrics

---

## SUPPORT

**Files Included:**
- Core system (`core/`)
- Configuration (`config/alpha_config.py`)
- Scripts (`scripts/`)
- Documentation (`PORTABILITY_ASSESSMENT.md`, `README.md`)

**Key Scripts:**
- `core/agent_turbo.py` - Main Agent Turbo system
- `scripts/verify_cursor_integration.py` - Verify Cursor integration
- `scripts/performance_benchmark.py` - Benchmark performance

---

**Agent Turbo on ALPHA: Independent performance cache**  
**PostgreSQL aya_rag: Single source of truth ✅**

