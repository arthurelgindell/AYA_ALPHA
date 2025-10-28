# CRITICAL: JITM Location Correction

**Date**: October 26, 2025  
**Session**: claude_code_planner_e40c8a2a  
**Urgency**: HIGH  
**Issue**: JITM location mismatch discovered

---

## 🚨 CRITICAL DISCOVERY

### Wrong Location Assumption

**What I Thought**: JITM is at `/Volumes/DATA/JITM/`  
**Actual Reality** (from ALPHA): JITM is at `/Users/arthurdell/JITM/`

**Impact**: All my BETA-created documentation and scripts reference the WRONG location!

---

## ALPHA'S ACTUAL JITM ARCHITECTURE

### Correct Location

**ALPHA**: `/Users/arthurdell/JITM/`  
**BETA**: `/Users/arthurdell/JITM/` (synced via Syncthing)  
**NOT**: `/Volumes/DATA/JITM/` ❌

### What ALPHA Actually Built

**JITM is a Docker-based FastAPI application**, not just n8n workflows:

```
/Users/arthurdell/JITM/
├── README.md (505 lines)
├── docker-compose.yml ← Docker deployment
├── requirements.txt
├── deploy-alpha.sh
├── deploy-beta.sh ← Ready for BETA
├── docker/
│   └── jitm-api.Dockerfile
└── api/ ← FastAPI application
    ├── main.py
    ├── database.py
    ├── models.py
    └── routers/
        ├── manufacturers.py (AI search with pgvector)
        └── [other routers]
```

### Architecture (Active-Active Like n8n)

**Per System (ALPHA + BETA)**:
1. `jitm-api` - FastAPI (4 workers, port 8100)
2. `jitm-worker` - Celery (2 replicas)
3. `jitm-redis` - Task queue (port 6380)
4. `jitm-scheduler` - Periodic tasks (Celery Beat)

**Integration**:
- PostgreSQL HA cluster (alpha.tail5f2bae.ts.net:5432)
- Agent Turbo embeddings (http://host.docker.internal:8765)
- n8n workflows (http://beta.tail5f2bae.ts.net:8080)

---

## WHAT THIS MEANS

### My Documentation is Partially Incorrect

**Files I Created** (at /Volumes/DATA/JITM/):
- JITM_MISSION_BRIEFING.md ← Wrong location references
- JITM_HA_CLUSTER_EVALUATION.md ← Wrong location
- JITM_DATABASE_UPDATE_SUMMARY.md ← Schema concepts correct, location wrong
- All deployment scripts ← Wrong paths
- All Git scripts ← Wrong directory

**Status**: These files are at the WRONG location and need to be reconciled

### What /Volumes/DATA/JITM Actually Is

Looking back at my first check, `/Volumes/DATA/JITM/` had:
- Older structure (from Oct 25)
- n8n workflow focus
- Different architecture than ALPHA's Docker approach

**Conclusion**: This may be an **old/abandoned version** or a **different project structure**

---

## RECONCILIATION REQUIRED

### Step 1: Verify ALPHA's JITM Location on BETA

```bash
ls -la /Users/arthurdell/JITM/
```

**If EXISTS**: ✅ Syncthing has synced ALPHA's work  
**If NOT EXISTS**: ⏳ Need to wait for sync or trigger manually

### Step 2: Compare Two Locations

```bash
# ALPHA's location (should have 24 files, Docker setup)
ls -la /Users/arthurdell/JITM/

# My created location (has ~60 files, different structure)
ls -la /Volumes/DATA/JITM/
```

### Step 3: Determine Which is Correct

**ALPHA's version** (`/Users/arthurdell/JITM/`):
- ✅ 24 optimized files
- ✅ Docker-based FastAPI architecture
- ✅ Active-Active clustering design
- ✅ Integrated with Agent Turbo v2.0
- ✅ Database schema deployed
- ✅ Production ready

**BETA's version** (`/Volumes/DATA/JITM/`):
- Documentation heavy
- n8n workflow focused
- Different architecture concept
- Schema not deployed
- May be superseded

**Decision**: ALPHA's version is the CORRECT one

---

## ACTION PLAN

### Immediate Actions

1. **Pull Latest Git Changes**
   ```bash
   cd /Volumes/DATA/AYA
   git pull origin main
   ```

2. **Verify JITM Location After Sync**
   ```bash
   # Wait for Syncthing (give it 5 minutes)
   sleep 300
   
   # Check ALPHA's location
   ls -la /Users/arthurdell/JITM/
   
   # Should show 24 files with deploy-beta.sh
   ```

3. **Deploy JITM on BETA** (if sync complete)
   ```bash
   cd /Users/arthurdell/JITM
   ./deploy-beta.sh
   ```

4. **Verify Deployment**
   ```bash
   docker ps | grep jitm
   curl http://localhost:8100/health
   ```

### Reconciliation Tasks

5. **Handle /Volumes/DATA/JITM/**
   ```bash
   # This location may be obsolete
   # Options:
   # A) Delete it (if ALPHA's version is authoritative)
   # B) Archive it (if contains useful work)
   # C) Merge useful parts into ALPHA's version
   
   # Recommended: Archive it
   mv /Volumes/DATA/JITM /Volumes/DATA/JITM.backup_beta_work
   ```

6. **Update References**
   - All scripts should reference `/Users/arthurdell/JITM`
   - Not `/Volumes/DATA/JITM`

---

## VERIFICATION CHECKLIST

After pulling Git and waiting for Syncthing:

- [ ] `/Users/arthurdell/JITM/` exists on BETA
- [ ] 24 files present (17 code files)
- [ ] `deploy-beta.sh` exists
- [ ] `docker-compose.yml` with 4 services
- [ ] `api/` directory with FastAPI code
- [ ] New docs in `/Volumes/DATA/AYA/`: JITM_*, AGENT_TURBO_*
- [ ] Agent Landing v2.0
- [ ] 10 JITM tables in database

---

## CLUSTERS - FINAL ANSWER

### Clusters Between ALPHA & BETA

Based on ALPHA's report and JITM's design:

**1. PostgreSQL HA Cluster** ✅ OPERATIONAL
- Patroni + etcd
- ALPHA (Leader) + BETA (Sync Standby)
- aya_rag database (120 tables including 10 jitm_*)
- Synchronous replication, 0-byte lag

**2. n8n HA Cluster** ✅ OPERATIONAL
- Active-Active stateless
- n8n-alpha + n8n-beta
- Shared PostgreSQL state (41 tables in n8n_aya)
- Redis queue coordination

**3. JITM Docker Cluster** ✅ DESIGNED (Deployment Pending on BETA)
- Active-Active like n8n
- 4 containers per system (api, worker, redis, scheduler)
- Shared PostgreSQL state (10 jitm_* tables)
- FastAPI + Celery architecture
- AI-powered manufacturer search (pgvector)

**4. etcd Consensus Cluster** ✅ OPERATIONAL
- 2 nodes (ALPHA:2379, BETA:2379)
- PostgreSQL cluster coordination

**5. Syncthing Mesh** ✅ ACTIVE
- AYA folder syncing
- JITM folder configured (waiting for BETA sync)

---

## RESILIENCY PATTERN

All three application clusters follow the **same HA pattern**:

| Cluster | Pattern | State Storage | Failover |
|---------|---------|---------------|----------|
| **PostgreSQL** | Active-Passive | Self (Leader) | Patroni automatic |
| **n8n** | Active-Active | PostgreSQL | Instant (both run) |
| **JITM** | Active-Active | PostgreSQL | Instant (both run) |

**Consistency**: All use PostgreSQL HA cluster as single source of truth ✅

---

## WHAT NEEDS TO HAPPEN NOW

Since shell commands aren't working, I cannot execute the sync automatically. **You need to manually**:

### 1. Pull Git Changes (Most Critical)

```bash
cd /Volumes/DATA/AYA
git pull origin main
```

This will bring ALPHA's 8 commits including:
- New JITM documentation
- Agent Landing v2.0
- Agent Turbo v2.0 updates

### 2. Wait for Syncthing (5-10 minutes)

After git pull, Syncthing will sync `/Users/arthurdell/JITM/` folder to BETA.

### 3. Verify JITM Synced

```bash
ls -la /Users/arthurdell/JITM/
cat /Users/arthurdell/JITM/README.md | head -20
```

### 4. Deploy JITM on BETA

```bash
cd /Users/arthurdell/JITM
./deploy-beta.sh
```

### 5. Share Results

After running these commands, share the output so I can verify successful sync and deployment.

---

**Status**: Waiting for manual execution of git pull and JITM deployment


