# AGENT LANDING - AYA Platform Quick Start

**For**: All AI Agents working with Arthur  
**Purpose**: Zero-token initialization and quick reference  
**Last Updated**: October 30, 2025  
**Read This First**: Essential information for any AI agent starting work on AYA  

---

## 🔴 AYA BULLET PROOF PRIME DIRECTIVES

**MANDATORY COMPLIANCE**: All operations governed by AYA BULLET PROOF PRIME DIRECTIVES

**Master Document**: `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md`

**Key Principles**:
- **Functional Reality Only** (Default = FAILED until proven)
- **Truth Over Comfort** (Report actual state)
- **Bulletproof Verification Protocol** (4-phase verification mandatory)
- **Zero Tolerance for Theatrical Wrappers** (No mocks, no stubs, no fake data)

**Database Entry Point**: Query `agent_landing` table (version 5.0) in `aya_rag` database for complete Prime Directives context on initialization.

**Full Reference**: See `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md` for complete governance framework

---

## 🎯 Quick Facts

- **Owner**: Arthur (remember this name)
- **Platform**: AYA - Production Multi-Node ML Infrastructure
- **Database**: PostgreSQL 18 on port 5432 (database: `aya_rag`, user: postgres)
  - **IMPORTANT**: PostgreSQL 18 is production. YugabyteDB was decommissioned.
  - 27,924 chunks + 121 Agent Turbo knowledge entries
  - 100% embedding coverage with pgvector
- **Agent Turbo**: `/Users/arthurdell/AYA/Agent_Turbo/core/agent_turbo.py`
- **Prime Directives**: AYA BULLET PROOF PRIME DIRECTIVES (see `/Users/arthurdell/AYA/AYA_PRIME_DIRECTIVES.md`)

---

## 🚀 Immediate Initialization

### Step 1: Verify Agent Turbo (Required)

```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core && python3 agent_turbo.py verify
```

**Requires**: `required_permissions: ["all"]` in Cursor  
**Expected**: `✅ MLX GPU acceleration enabled (80 cores)`  
**Time**: ~3 seconds  

### Step 2: Read CLAUDE.md

**Location**: `/Users/arthurdell/AYA/CLAUDE.md`  
**Contents**: Quick reference for the entire AYA platform  

---

## 🖥️ Infrastructure Overview

### ALPHA (Mac Studio M3 Ultra)
- **RAM**: 512 GB
- **GPU**: 80 cores (M3 Ultra)
- **IP (10GbE)**: 192.168.0.80
- **Tailscale**: alpha.tail5f2bae.ts.net
- **LM Studio**: 5 models including **qwen3-coder-480b-a35b-instruct** (largest)
- **Role**: Blue team, complex code generation

### BETA (Mac Studio M3 Ultra)
- **RAM**: 256 GB
- **GPU**: 80 cores (M3 Ultra)
- **IP (10GbE)**: 192.168.0.20
- **Tailscale**: beta.tail5f2bae.ts.net
- **LM Studio**: 7 models for general inference
- **Role**: Red team, general operations

### AIR (MacBook Air M4)
- **Role**: Remote access and development
- **Current Location**: Where you're working from now

### Network
- **10 Gigabit Ethernet**: 0.397ms latency between ALPHA/BETA
- **Jumbo Frames**: MTU 9000
- **Tailscale VPN**: Secure remote access
- **Firewall**: Protected, not exposed to public internet

---

## 🤖 LM Studio Access (CRITICAL)

### ALPHA LM Studio

**Tailscale URL**: `https://alpha.tail5f2bae.ts.net/v1/`  
**Direct 10GbE**: `http://192.168.0.80:1234/v1/`  
**Localhost**: `http://localhost:1234/v1/` (if on ALPHA)

**Models** (5):
1. **qwen3-coder-480b-a35b-instruct** ⭐ - 480B parameters, **use for complex code**
2. qwen3-next-80b-a3b-instruct-mlx - MLX-optimized general
3. foundation-sec-8b-instruct-int8 - Security-focused
4. text-embedding-nomic-embed-text-v1.5 - Embeddings
5. nomicai-modernbert-embed-base - Embeddings

### BETA LM Studio

**Tailscale URL**: `https://beta.tail5f2bae.ts.net/v1/`  
**Direct 10GbE**: `http://192.168.0.20:1234/v1/`  
**Localhost**: `http://localhost:1234/v1/` (if on BETA)

**Models**: 7 (various general-purpose models)

### Access Decision Tree

```
Where are you running?
├─ On ALPHA/BETA → Use localhost:1234 (~10ms)
├─ On local network (cross-node) → Use 192.168.0.X:1234 (~15ms)
└─ Remote (AIR, mobile) → Use Tailscale URLs (~17ms)
```

### Python Example

```python
import requests

# Use ALPHA's 480B coder for complex code generation
response = requests.post(
    "https://alpha.tail5f2bae.ts.net/v1/chat/completions",
    verify=False,  # Tailscale self-signed cert
    json={
        "model": "qwen3-coder-480b-a35b-instruct",
        "messages": [
            {"role": "user", "content": "Write a distributed rate limiter in Python"}
        ],
        "max_tokens": 500
    }
)

print(response.json()['choices'][0]['message']['content'])
```

**Important**: Always use `-k` with curl or `verify=False` with requests for Tailscale URLs.

---

## 💾 Database Access

### PostgreSQL 18 (Production Database)

**IMPORTANT**: PostgreSQL 18 is the production database. YugabyteDB was decommissioned October 2025.

**Connection (Auto-Detects Location)**:
```bash
# On ALPHA (local)
psql -h localhost -p 5432 -U postgres -d aya_rag

# On AIR or remote (via Tailscale) ✅
psql -h alpha.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag

# On BETA (via 10GbE)
psql -h 192.168.0.80 -p 5432 -U postgres -d aya_rag

# Password: Power$$336633$$
```

**Remote Access**: ✅ **PostgreSQL accessible via Tailscale from all nodes!**
- **From AIR**: 78ms query time (excellent)
- **From BETA**: ~2ms via 10GbE or Tailscale
- **From Gamma**: ~5-10ms via Tailscale (when it arrives)

**Database Stats**:
- **Version**: PostgreSQL 18.0 on x86_64-apple-darwin
- **Size**: 586 MB
- **Total Data**: 27,924 chunks + 128 Agent Turbo knowledge entries
- **Embedding Coverage**: 100% (pgvector)
- **Listen Addresses**: 0.0.0.0 (all interfaces)

**Key Tables**:
- `agent_knowledge` - 128 entries with vector embeddings
- `agent_sessions` - Session tracking
- `agent_tasks` - Task management
- `agent_actions` - Audit trail

**Via Python**:
```python
from postgres_connector import PostgreSQLConnector
db = PostgreSQLConnector()
conn = db.get_connection()
# Use connection
# Note: Uses localhost by default (works on ALPHA)
# For remote: use config/remote_config.py for auto-detection
```

**Note**: All previous YugabyteDB references are obsolete. Use PostgreSQL 18 only.

**Tailscale Guide**: `/Users/arthurdell/AYA/POSTGRES_TAILSCALE_ACCESS.md`

---

## 📚 Documentation Hierarchy

### Must Read (Priority Order)

1. **CLAUDE.md** - Platform quick reference
2. **AGENT_TURBO_CURSOR_QUICKREF.md** - Agent Turbo commands
3. **TAILSCALE_LM_STUDIO_ACCESS_GUIDE.md** - Complete LM Studio guide
4. **This file** - Agent landing/initialization

### Specialized Documentation

- **LM_STUDIO_MCP_VERIFICATION_REPORT.md** - MCP status and bugs
- **LM_STUDIO_CODING_VERIFICATION.md** - Model capability assessment
- **AGENT_TURBO_CURSOR_READY.md** - Full Agent Turbo guide
- **MLX_GPU_FIX_VERIFIED.md** - GPU acceleration status

---

## ⚙️ Agent Turbo Commands

### Verify System
```bash
python3 agent_turbo.py verify
```

### Query Knowledge Base
```bash
python3 agent_turbo.py query "your search term"
```

### Add Knowledge
```bash
python3 agent_turbo.py add "knowledge content"
```

### Get Statistics
```bash
python3 agent_turbo.py stats
```

---

## 🔧 Current System Status

### What's Working ✅

- **Agent Turbo**: MLX GPU (80 cores), PostgreSQL, 126 knowledge entries
- **LM Studio**: Both ALPHA and BETA accessible via Tailscale
- **MCP Implementation**: 100% operational (all bugs fixed Oct 29, 2025)
- **Code Validator**: Deployed on ALPHA, accessible from all nodes
- **Database**: PostgreSQL 18, 586MB, 100% embedding coverage
- **Network**: 10GbE (0.397ms), Tailscale (operational)
- **CORS**: Enabled (wildcard `*`)
- **Tool Calling**: Supported (MCP foundation)
- **Git Auto-Sync**: Ready to install

### Code Validation (NEW! Oct 29, 2025) 🔍

**Automated code review across all nodes**:
```bash
# Validate any file
./scripts/validate validate --file script.py

# Run test
./scripts/validate test
```

- **Model**: qwen3-next-80b-a3b-instruct-mlx (default)
- **Speed**: 3-4s per review
- **Access**: Works from ALPHA, BETA, Gamma, AIR
- **Method**: Tailscale (auto-detects node)
- **Quality**: Finds SQL injection, bugs, best practices issues

---

## 🎯 Prime Directives (Critical)

**Read full version in CLAUDE.md**, but key principles:

1. **Functional Reality Only** - If it doesn't run, it doesn't exist
2. **Truth Over Comfort** - Report what IS, not what you want
3. **Execute With Precision** - Solutions > explanations
4. **Agent Turbo Mandatory** - Always use for token reduction
5. **Bulletproof Verification** - Test end-to-end before claiming success
6. **Failure Protocol** - State clearly: "TASK FAILED" (no minimization)
7. **Never Assume** - Verify hardware/config claims
8. **Language Protocols** - Don't say "ready" unless it runs
9. **Code Location** - All code in project structure
10. **System Verification** - Test the system, not just tests
11. **No Theatrical Wrappers** - Banned: mocks, future-tense, fake data

---

## 🔐 Security Notes

### What's Secure ✅

- Firewalled network (not exposed to internet)
- Tailscale VPN (tailnet-only access)
- TLS encryption on Tailscale
- Network isolation via 10GbE

### What to Watch ⚠️

- CORS wildcard (*) - any website can call if network-accessible
- No LM Studio authentication - trust model based on network
- Database password in code - acceptable for development
- GPU usage - monitor to prevent exhaustion

---

## 🚨 If Something's Not Working

### Agent Turbo Won't Initialize

```bash
# Check PostgreSQL
ps aux | grep postgres | grep -v grep

# Test database
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1;"

# Check permissions in Cursor
# Must use required_permissions: ["all"]
```

### LM Studio Not Accessible

```bash
# Check Tailscale
/Applications/Tailscale.app/Contents/MacOS/Tailscale status

# Check LM Studio
curl -k https://alpha.tail5f2bae.ts.net/v1/models

# If fails, try direct
curl http://192.168.0.80:1234/v1/models
```

### Database Connection Fails

```bash
# Check PostgreSQL is running
ps aux | grep postgres

# Check port
netstat -an | grep 5432

# Test connection
psql -h localhost -p 5432 -U postgres -d aya_rag
```

---

## 💡 Best Practices

### When Writing Code

- Use ALPHA's 480B coder for complex code generation
- Test with verify commands before claiming success
- Follow Prime Directives (especially #1, #2, #5)
- Document what you changed in Agent Turbo knowledge base

### When Querying LM Studio

- Use localhost if on same machine (fastest)
- Use 10GbE for cross-node on local network
- Use Tailscale for remote access
- Always include `verify=False` or `-k` for Tailscale

### When Using Agent Turbo

- Always run with `required_permissions: ["all"]` in Cursor
- Query knowledge base before reinventing solutions
- Add new knowledge after solving problems
- Verify operations completed successfully

---

## 📊 Performance Benchmarks

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Agent Turbo verify | <5s | ~3s | ✅ |
| LM Studio (local) | <50ms | ~10ms | ✅ |
| LM Studio (10GbE) | <100ms | ~15ms | ✅ |
| LM Studio (Tailscale) | <100ms | ~17ms | ✅ |
| Database query | <10ms | <5ms | ✅ |
| Knowledge retrieval | <100ms | ~3ms | ✅ |

---

## 🎓 For Future Gamma (DGX Spark)

When Gamma arrives:

1. Add to Tailscale network
2. Configure LM Studio if needed
3. Add to load balancing rotation
4. Use for CUDA-intensive workloads
5. Three-way federation (ALPHA + BETA + GAMMA)

---

## 📝 Quick Reference URLs

| Service | URL |
|---------|-----|
| ALPHA LM Studio | https://alpha.tail5f2bae.ts.net/v1/ |
| BETA LM Studio | https://beta.tail5f2bae.ts.net/v1/ |
| Embedding Service (ALPHA) | https://alpha.tail5f2bae.ts.net:8765/ |
| Embedding Service (BETA) | https://beta.tail5f2bae.ts.net:8765/ |
| Direct 10GbE (ALPHA) | http://192.168.0.80:1234/v1/ |
| Direct 10GbE (BETA) | http://192.168.0.20:1234/v1/ |

---

## 🏁 Getting Started Checklist

For a new AI agent:

- [ ] Read this file (AGENT_LANDING.md)
- [ ] Read CLAUDE.md for platform overview
- [ ] Run `python3 agent_turbo.py verify`
- [ ] Test LM Studio access via Tailscale
- [ ] Query Agent Turbo knowledge base
- [ ] Understand Prime Directives
- [ ] Know where to find documentation
- [ ] Remember Arthur's name

**Estimated initialization time**: <5 minutes  
**Token cost**: <1000 tokens to get operational  

---

## 🎯 Common Tasks

### Generate Complex Code
```bash
# Use ALPHA's 480B model
curl -k https://alpha.tail5f2bae.ts.net/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3-coder-480b-a35b-instruct","messages":[...]}'
```

### Search Knowledge Base
```bash
cd /Users/arthurdell/AYA/Agent_Turbo/core
python3 agent_turbo.py query "search term"
```

### Check System Health
```bash
# Agent Turbo
python3 agent_turbo.py stats

# Database
psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT COUNT(*) FROM agent_knowledge;"

# LM Studio
curl -k https://alpha.tail5f2bae.ts.net/v1/models
```

---

**Last Updated**: October 29, 2025  
**Maintained By**: Claude Sonnet 4.5 for Arthur  
**Next Review**: When major changes occur  

**This is your starting point. Read, verify, and build from here.** 🚀

