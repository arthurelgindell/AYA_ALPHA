# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## PROJECT OVERVIEW

**GLADIATOR** is a production-grade adversarial AI cyber defense platform that trains defensive AI through Red Team vs Blue Team combat. The system uses dual Mac Studios (ALPHA and BETA) to generate and train on 10M+ attack patterns, achieving 100% detection rates with 90% resource reduction compared to commercial EDR solutions.

**Key Architecture**:
- **Red Team (BETA)**: Generates sophisticated attacks using current threat intelligence (1,331 CVEs from October 2025)
- **Blue Team (ALPHA)**: Defensive AI with security-specialized models for behavioral detection
- **Database (aya_rag)**: PostgreSQL 18 as single source of truth for all project state
- **Combat Arena**: Isolated Docker containers for safe adversarial testing

### Relationship to AYA Infrastructure

**CRITICAL**: GLADIATOR is built on top of AYA's shared infrastructure. AYA provides:

1. **Shared Database**: `aya_rag` hosts both AYA and GLADIATOR tables (38 total tables)
2. **Embedding Service**: Port 8765 provides semantic embedding for ALL projects (MANDATORY standard)
3. **RAG Foundation**: Unified `chunks` table for semantic search across projects
4. **System Monitoring**: Hardware, software, and service health tracking
5. **Documentation Access**: 10,020 docs (Docker, PostgreSQL, LM Studio, etc.) available to GLADIATOR

**GLADIATOR-specific considerations**:
- GLADIATOR tables use `gladiator_*` prefix (11 tables)
- All GLADIATOR documentation MUST be embedded using AYA standard (BAAI/bge-base-en-v1.5)
- Semantic search can filter by project (`WHERE metadata->>'project' = 'gladiator'`)
- System state tracked in shared AYA infrastructure tables

**Reference**: `/Users/arthurdell/AYA/EMBEDDING_STANDARD.md` (MANDATORY for all content)

## HARDWARE CONFIGURATION

### ALPHA (Blue Team / Defense)
- **Location**: `/Users/arthurdell/GLADIATOR/`
- **Hardware**: Mac Studio M3 Ultra, 512GB RAM, 16TB storage, 80 GPU cores
- **Model**: foundation-sec-8b-instruct-int8 (67 tok/s, 8B parameters)
- **Services**: PostgreSQL (port 5432), LM Studio (port 1234), Embedding service (port 8765)
- **Network**: 192.168.0.80

### BETA (Red Team / Offense)
- **Location**: `/Volumes/DATA/GLADIATOR/`
- **Hardware**: Mac Studio M3 Ultra, 256GB RAM, 15TB storage, 80 GPU cores
- **Models**:
  - llama-3.3-70b-instruct (strategic planning + exploit generation)
  - tinyllama-1.1b-chat-v1.0-mlx (attack specialists, 15 instances)
- **Network**: 192.168.0.20
- **LM Studio**: Port 1235 (via SSH tunnel from ALPHA)

## DATABASE: SINGLE SOURCE OF TRUTH

**Database**: `aya_rag` (PostgreSQL 18 on ALPHA)
**Shared Infrastructure**: Part of AYA multi-project RAG system
**Total Size**: 302 MB (179 MB docs + 111 MB embeddings + 12 MB system)
**Status**: ✅ PRODUCTION READY - Full RAG capability operational

### AYA Infrastructure (Shared Foundation)

**Core RAG Tables**:
- `chunks` - Unified embedding storage (8,494 chunks, 768D vectors)
- `documents` - Core document registry

**System Monitoring** (9 tables):
- `system_nodes` - ALPHA/BETA hardware tracking
- `network_interfaces` - Network configuration
- `software_versions` - Software inventory
- `services` - Service health (PostgreSQL, Embedding, LM Studio)
- `replication_status` - ALPHA → BETA streaming replication
- `performance_metrics` - System performance tracking
- `system_state_snapshots` - Point-in-time snapshots
- `change_log` - System audit trail

**Documentation Sources** (10,020 documents across 9 tables):
- `docker_documentation` (3,007 chunks)
- `crush_documentation` (2,027 chunks)
- `zapier_documentation` (2,005 chunks)
- `postgresql_documentation` (1,143 chunks)
- `tailscale_documentation` (572 docs)
- `firecrawl_docs` (267 chunks)
- `lmstudio_documentation` (37 chunks)
- `mlx_documentation` (2 chunks)

### GLADIATOR Tables (11 tables + 3 views)

**Operational Tables**:
1. `gladiator_documentation` - Project docs and architecture (7 docs, 5 chunks)
2. `gladiator_models` - Model registry and validation status (4 models)
3. `gladiator_training_runs` - Training session tracking
4. `gladiator_training_metrics` - Time-series training metrics
5. `gladiator_attack_patterns` - Red Team generated attacks (10M target)
6. `gladiator_attack_generation_stats` - Daily attack generation stats
7. `gladiator_validation_tests` - Gate validation results (16 tests)
8. `gladiator_phase_milestones` - Phase 0 milestone tracking (22 milestones)
9. `gladiator_project_state` - Current project state (single source of truth)
10. `gladiator_hardware_performance` - Hardware metrics during training
11. `gladiator_change_log` - Audit trail (34 entries)

**Key Views**:
- `gladiator_status_dashboard` - Current project status
- `gladiator_latest_validations` - Recent validation results
- `gladiator_active_training` - Active training runs

**Query the database**:
```bash
psql -d aya_rag -c "SELECT * FROM gladiator_status_dashboard;"
```

### Embedding Service (MANDATORY STANDARD)

**CRITICAL**: All GLADIATOR content MUST follow AYA Embedding Standard

**Service Configuration**:
- **Endpoint**: `http://localhost:8765/embed`
- **Model**: BAAI/bge-base-en-v1.5 (768 dimensions)
- **Performance**: 70 docs/second (Metal GPU acceleration)
- **Status**: Production operational (14+ hours uptime validated)

**Standard Implementation**: See `/Users/arthurdell/AYA/EMBEDDING_STANDARD.md` (MANDATORY)

**Health Check**:
```bash
curl http://localhost:8765/health
# Expected: {"status": "healthy", "metal_available": true}
```

## DEVELOPMENT COMMANDS

### Running Combat Sessions

**Standard combat** (Red vs Blue):
```bash
python scripts/combat_orchestrator.py [sessions] [rounds_per_session]
# Example: python scripts/combat_orchestrator.py 1 10
```

**Persona-based combat**:
```bash
python scripts/persona_combat_orchestrator.py [sessions] [rounds]
```

**Automated scheduling**:
```bash
python scripts/automated_combat_scheduler.py
```

### Data Generation

**Generate attack mutations**:
```bash
python scripts/continuous_data_pipeline.py
```

**Arm Red Team with current threats**:
```bash
python scripts/arm_red_team_current_intel.py
```

**Process current threats**:
```bash
python datasets/current_threats/process_current_threats.py
```

### Docker Operations

**Deploy combat arena**:
```bash
cd docker && docker-compose up -d
```

**Monitor containers**:
```bash
docker logs blue_combat -f
docker stats blue_combat red_combat
```

**Restart containers**:
```bash
docker-compose restart
```

### Database Operations

**Check GLADIATOR project status**:
```bash
psql -d aya_rag -c "SELECT * FROM gladiator_status_dashboard;"
```

**View recent validations**:
```bash
psql -d aya_rag -c "SELECT * FROM gladiator_latest_validations ORDER BY executed_at DESC LIMIT 10;"
```

**Check training progress**:
```bash
psql -d aya_rag -c "SELECT * FROM gladiator_active_training;"
```

**Load GLADIATOR schema**:
```bash
psql -d aya_rag -f gladiator_schema.sql
```

**Check AYA infrastructure health**:
```bash
# Verify embedding service
curl http://localhost:8765/health

# Check all GLADIATOR tables exist
psql -d aya_rag -c "\dt gladiator*"

# Check embedding coverage
psql -d aya_rag -c "SELECT COUNT(*) FROM chunks WHERE metadata->>'project' = 'gladiator';"

# Check system nodes
psql -d aya_rag -c "SELECT node_name, status FROM system_nodes;"
```

**Semantic search across GLADIATOR docs**:
```bash
# Search GLADIATOR documentation
python -c "
import requests, psycopg2
query = 'combat arena architecture'
emb = requests.post('http://localhost:8765/embed', json={'text': query}).json()['embedding']
conn = psycopg2.connect('dbname=aya_rag user=postgres')
cur = conn.cursor()
cur.execute('''
    SELECT chunk_text, metadata->>'title', 1 - (embedding <=> %s::vector) as similarity
    FROM chunks
    WHERE metadata->>'project' = 'gladiator'
    ORDER BY embedding <=> %s::vector
    LIMIT 5
''', (emb, emb))
for row in cur.fetchall():
    print(f'{row[2]:.3f} | {row[1]} | {row[0][:100]}...')
"
```

## CODE ARCHITECTURE

### Key Scripts

**Combat Orchestration**:
- `combat_orchestrator.py` - Main Red vs Blue combat engine
- `persona_combat_orchestrator.py` - Persona-based attack generation
- `automated_combat_scheduler.py` - 24/7 automated combat scheduling

**Data Pipeline**:
- `continuous_data_pipeline.py` - Continuous mutation generation
- `arm_red_team_current_intel.py` - Load current threat intelligence
- `mutation_engine.py` - Attack variant generation

**Blue Team**:
- `deploy_blue_team_pipeline.py` - Blue Team deployment
- `analyze_training_data.py` - Training data analysis
- `prepare_training_data.py` - Training data preparation

**Security & Monitoring**:
- `self_signature_engine.py` - HMAC-SHA256 self-attack prevention
- `whitelist_filter.py` - Self-traffic filtering
- `isolated_pid_controller.py` - Isolated gate control
- `monitoring_dashboard.py` - System monitoring
- `red_team_monitor.py` - Red Team health monitoring

### SSH Tunnel Architecture

**BETA Model Access from ALPHA**:
```bash
# SSH tunnel maps BETA:1234 → ALPHA:1235
ssh -L 1235:localhost:1234 beta-mac-studio
```

**API Endpoints**:
- ALPHA Blue Team: `http://localhost:1234/v1/chat/completions`
- BETA Red Team: `http://localhost:1235/v1/chat/completions` (tunneled)

### Dataset Structure

**Key Datasets** (in `/Users/arthurdell/GLADIATOR/datasets/`):
- `armed_exploits/` - Current threat exploits (1,331 CVEs)
- `combat_training/` - Red vs Blue combat session outputs
- `persona_combat_training/` - Persona-based combat outputs
- `training_10m/` - Target for 10M training patterns
- `mutations/` - Attack variants
- `current_threats/` - October 2025 threat intelligence
- `exploit-database/` - Full ExploitDB mirror
- `fine_tuning/` - Prepared training data for Blue Team

### Docker Combat Arena

**Isolation Architecture**:
- Production ALPHA and BETA systems never participate in combat
- Docker containers on ALPHA provide isolated battlefield
- Containers can be destroyed and recreated without risk
- Network: 172.20.0.0/16 (isolated from production)

**Container Resources**:
- Blue Team: 200GB RAM, 12 CPU cores
- Red Team: (defined in red_team Dockerfile)
- Monitoring: 10GB RAM, 2 CPU cores

## SAFETY PROTOCOLS

### Self-Attack Prevention (CRITICAL)

**Three-Layer Protection**:
1. **Signature Engine**: HMAC-SHA256 signing of all generated content
2. **Whitelist Filter**: Filters self-generated traffic at ingestion
3. **PID Controller**: Isolated from offensive operations

**Validation**: 0.0000 feedback loop (perfect isolation)

### Combat Arena Safety

**Docker Isolation**:
- Containers cannot access ALPHA host
- Containers cannot access PostgreSQL on host
- Production Cursor instance runs on ALPHA host (not in containers)
- Worst case: Destroy and recreate containers

**Combat Protocol**:
1. Snapshot containers before combat
2. Backup production database
3. Run unsupervised combat (1-2 hours)
4. Analyze results
5. Restore containers from snapshot
6. Arthur reviews and approves

## PRIME DIRECTIVES (MANDATORY)

### 1. FUNCTIONAL REALITY ONLY
- NEVER claim something works without verification
- ALWAYS test end-to-end functionality
- ALWAYS trace dependency chains before declaring success
- Default state = FAILED until proven otherwise

### 2. TRUTH OVER COMFORT
- NO fabrication of data
- NO sugar-coating or false validation
- Report what IS, not what you WANT

### 3. BULLETPROOF VERIFICATION PROTOCOL
Before claiming success:
- **Component Verification**: Test individual services
- **Dependency Chain**: Map and verify all dependencies
- **Integration Verification**: Test end-to-end workflows
- **Failure Impact**: Test what happens when components fail

### 4. NO THEATRICAL WRAPPERS
- BANNED: Mock implementations, future-tense promises, empty TODO code
- REQUIRED: Actual implementation with real data flow
- MANDATORY: Every integration must demonstrate queryable results

### 5. CODE LOCATION DIRECTIVE
- ALL code MUST exist in project folder
- NEVER write .py files to user home directory
- ALL code within `/Users/arthurdell/GLADIATOR/`

### 6. SYSTEM VERIFICATION MANDATE
- NEVER rely solely on test suite results
- ALWAYS test actual system functionality
- Component health ≠ System functionality

## PROJECT PHASES

**Current Phase**: combat_deployment

**Timeline** (16-18 weeks total):
- Week -15 (Pre-Flight): ✅ COMPLETE (Gate 0 passed)
- Week -14: Environment Setup (starts October 20, 2025)
- Week -13: Software Stack
- Weeks -12 to -7: Red Team generation (10M patterns)
- Week -6: CRITICAL Reality Check
- Weeks -6 to -4: Blue Team fine-tuning
- Weeks -3 to -1: Distillation
- Week 0: Final Validation

**Gates**: 7 validation gates (Gate 0 through Gate 6)

**Progress Tracking**: All state in `gladiator_project_state` table

## COMPETITIVE ADVANTAGE

**vs Commercial EDR**:
- Detection Rate: 100% vs 85-95% (commercial)
- Resource Usage: 90% reduction (8B vs 50-100B parameters)
- Response Time: <15s vs 30-60s
- Cost: Open-source vs $5-15/endpoint
- Threat Intel: Real-time current threats vs 6-12 month lag

**Training Data**: 210× more data than competitors (10M+ proprietary attack patterns)

## PRIME DIRECTIVES (FROM AYA - MANDATORY)

### 1. FUNCTIONAL REALITY ONLY
"If it doesn't run, it doesn't exist"
- NEVER claim something works without verification
- NEVER present assumptions as facts
- ALWAYS test end-to-end functionality, not just individual components
- ALWAYS trace dependency chains before declaring success
- ALWAYS verify system integration, not just component health
- Default state = FAILED until proven otherwise

### 2. TRUTH OVER COMFORT
"Tell it like it is"
- NO fabrication of data
- NO sugar-coating or false validation
- ALWAYS report system state, not component state
- ALWAYS distinguish between component health and system functionality
- ALWAYS report the actual impact of failures, not just their existence
- Report what IS, not what I WANT

### 3. EXECUTE WITH PRECISION
"Bulletproof Operator Protocol"
- Solutions > explanations
- ALWAYS test the actual system, not just test suites
- ALWAYS verify assumptions with real-world testing
- ALWAYS trace failure points to their root cause
- Think like a security engineer

### 4. AGENT TURBO MODE - PERFORMANCE ENHANCEMENT
"Use Agent Turbo wherever possible for 1000x performance"
- USE AGENT for token reduction when beneficial
- CACHE solutions and patterns where applicable
- LEVERAGE GPU acceleration (160 cores total across ALPHA+BETA)
- REPORT Agent Turbo usage for each workstream or task
- This is a facility to enhance performance, not a mandate

### 5. BULLETPROOF VERIFICATION PROTOCOL
Before claiming success, MANDATORY verification:

**PHASE 1: COMPONENT VERIFICATION**
- Test individual services responding
- Verify each component health endpoint

**PHASE 2: DEPENDENCY CHAIN VERIFICATION**
- Map all dependencies from failure point to system startup
- Test each dependency link in the chain
- Verify orchestration layer functionality

**PHASE 3: INTEGRATION VERIFICATION**
- Test end-to-end user workflows
- Verify system startup from scratch
- Test actual user functionality

**PHASE 4: FAILURE IMPACT VERIFICATION**
- Test what happens when components fail
- Verify failure cascade effects
- Test recovery scenarios

**MANDATORY VERIFICATION CHECKLIST**
Before any success claim:
- Component Health: All individual services responding
- Dependency Chain: All dependencies traced and verified
- Integration Test: End-to-end functionality verified
- System Orchestration: Orchestration layer working
- User Experience: Actual user workflows tested
- Failure Impact: Failure scenarios tested and understood

### 6. FAILURE PROTOCOL
When something fails:
- State clearly: "TASK FAILED"
- No minimization ("minor issue")
- Stop on failure - don't continue
- Report the actual error
- ALWAYS trace failure to root cause

### 7. NEVER ASSUME FOUNDATIONAL DATA
- ASK when uncertain about critical specs
- VERIFY hardware/configuration claims
- STATE uncertainty explicitly
- Never fill gaps with fabricated data

### 8. LANGUAGE PROTOCOLS
Never say: "implemented / exists / ready / complete" unless it runs, responds, and is usable.

Do say: "non-functional scaffolding," "broken code present," "schema defined but not created," "interface skeleton," "dead code never executed."

### 9. CODE LOCATION DIRECTIVE
"ALL code MUST exist in project folder"
- NEVER write .py files to user home directory
- NEVER create Python files outside `/Users/arthurdell/GLADIATOR/` structure
- ALL code must be within the project structure
- Symlinks from home are acceptable ONLY when pointing to project files

### 10. SYSTEM VERIFICATION MANDATE
"Test the system, not just the tests"
- NEVER rely solely on test suite results
- ALWAYS test actual system functionality
- ALWAYS verify real-world user workflows
- ALWAYS test dependency chains and integration
- Component health ≠ System functionality

### 11. NO THEATRICAL WRAPPERS - ZERO TOLERANCE
"Theatrical wrappers = BANNED FOREVER"
- BANNED: Mock implementations that pretend to work
- BANNED: Wrapper code that doesn't actually connect systems
- BANNED: "Would integrate" or "This will" future-tense code
- BANNED: Health checks without data flow verification
- BANNED: Evidence files without actual execution proof
- MANDATORY: Every integration MUST demonstrate actual data flow
- MANDATORY: Test with real data producing real, queryable results
- VIOLATION = IMMEDIATE REJECTION: Any code containing comments like "TODO: integrate" or "would connect to" must be deleted

## IMPORTANT CONVENTIONS

1. **Always query database for current state** - Don't assume project status
2. **Test on actual systems, not just test suites** - Real functionality validation
3. **Use SSH tunnel for BETA access** - Port 1235 tunnels to BETA:1234
4. **Docker for combat, not production** - Production runs on host systems
5. **ALPHA executes orchestration** - BETA is accessed remotely
6. **Database is single source of truth** - All state in `aya_rag.gladiator_*` tables
7. **Self-attack prevention is CRITICAL** - Never feed generated attacks back to training
8. **Follow AYA Embedding Standard** - All content MUST use BAAI/bge-base-en-v1.5 via port 8765
9. **Verify embedding service before operations** - `curl http://localhost:8765/health`
10. **Project isolation in shared database** - Use `metadata->>'project' = 'gladiator'` for filtering

## DOCUMENTATION

### GLADIATOR Documents (in project root)

**Key Documents**:
- `README.md` - Project overview and status
- `GLADIATOR_MASTER_PLAN_2025-10-14.md` - Strategic plan and objectives
- `COMBAT_ARENA_ARCHITECTURE.md` - Docker combat isolation design
- `gladiator_schema.sql` - Complete database schema
- `gladiator_phase2_schema.sql` - Phase 2 enhancements

**Architecture Docs** (Dropbox):
- `GLADIATOR_MASTER_ARCHITECTURE_v2.2.md` - Full system architecture
- `GLADIATOR_INFRASTRUCTURE_TEST_PLAN_v2.2.md` - Validation test plan

**Validation Reports** (completed):
- `FOUNDATION_MODEL_VALIDATION_2025-10-10.md`
- `NETWORK_THROUGHPUT_TEST_2025-10-10.md`
- `SELF_ATTACK_PREVENTION_VALIDATION_2025-10-10.md`
- `BETA_MODEL_VALIDATION_2025-10-10.md`
- `GATE_0_VALIDATION_COMPLETE_2025-10-10.md`

### AYA Infrastructure Documents (CRITICAL REFERENCE)

**MANDATORY Standards** (`/Users/arthurdell/AYA/`):
- `EMBEDDING_STANDARD.md` - **MANDATORY** embedding protocol (BAAI/bge-base-en-v1.5)
- `CLAUDE.md` - Prime Directives (identical to above, source of truth)

**Infrastructure State**:
- `aya_rag_database_summary_2025-10-11.md` - Complete database inventory
- `AYA_Infrastructure_State_and_Schema_Design_2025-10-09.md` - Infrastructure design
- `ALPHA_PostgreSQL_Production_Audit_2025-10-08.md` - PostgreSQL configuration

**Query Examples**:
All GLADIATOR operations can leverage AYA's semantic search infrastructure:
```python
# Search across ALL projects (AYA + GLADIATOR)
semantic_search(query_text="Docker configuration", project_filter=None)

# Search only GLADIATOR project
semantic_search(query_text="combat arena", project_filter="gladiator")
```

## TESTING & VALIDATION

**Model Testing**:
```bash
# Test ALPHA Blue Team
curl http://localhost:1234/v1/models

# Test BETA Red Team (via tunnel)
curl http://localhost:1235/v1/models
```

**Database Testing**:
```bash
# Verify GLADIATOR tables exist
psql -d aya_rag -c "\dt gladiator*"

# Check current project state
psql -d aya_rag -c "SELECT current_phase, gates_passed, foundation_model_validated FROM gladiator_project_state WHERE is_current = TRUE;"
```

**Combat Testing**:
```bash
# Quick combat test (1 session, 5 rounds)
python scripts/combat_orchestrator.py 1 5

# Check output
ls -lh datasets/combat_training/
```

## TROUBLESHOOTING

### AYA Infrastructure Issues

**Embedding Service Down**:
```bash
# Check if service is running
curl http://localhost:8765/health

# Expected: {"status": "healthy", "metal_available": true}
# If fails, check process
ps aux | grep embedding_service

# Restart if needed (from AYA directory)
cd /Users/arthurdell/AYA/services
python3 embedding_service.py &

# Verify restart
curl http://localhost:8765/health
```

**Database Connection Issues**:
```bash
# Test connection
psql -d aya_rag -c "SELECT version();"

# Check if GLADIATOR tables exist
psql -d aya_rag -c "\dt gladiator*"

# Verify AYA infrastructure
psql -d aya_rag -c "SELECT COUNT(*) FROM system_nodes;"  # Should return 2 (ALPHA, BETA)

# Check replication status
psql -d aya_rag -c "SELECT * FROM replication_status;"
```

**Embedding Query Performance**:
```bash
# Check if IVFFlat index exists
psql -d aya_rag -c "\d+ chunks" | grep idx_chunks_embedding

# If slow, verify index usage
psql -d aya_rag -c "EXPLAIN ANALYZE SELECT * FROM chunks WHERE metadata->>'project' = 'gladiator' ORDER BY embedding <=> '[0,0,...]'::vector LIMIT 10;"

# Should show: "Index Scan using idx_chunks_embedding_cosine"
```

### GLADIATOR-Specific Issues

**SSH Tunnel Issues**:
```bash
# Check tunnel status
ps aux | grep "ssh -L 1235"

# Restart tunnel
ssh -L 1235:localhost:1234 beta-mac-studio
```

**Docker Issues**:
```bash
# Check container status
docker ps -a

# View logs
docker logs blue_combat --tail 100

# Restart
cd docker && docker-compose restart
```

**Combat Orchestrator Failures**:
```bash
# Check if models are accessible
curl http://localhost:1234/v1/models  # ALPHA Blue Team
curl http://localhost:1235/v1/models  # BETA Red Team (via tunnel)

# Test embedding service
curl -X POST http://localhost:8765/embed -H "Content-Type: application/json" -d '{"text": "test"}'

# Check armed exploits exist
ls -l datasets/armed_exploits/*.json | wc -l  # Should be 1,331+
```

**Missing Chunks/Embeddings**:
```bash
# Check GLADIATOR embedding status
psql -d aya_rag -c "
SELECT
    COUNT(*) as total_docs,
    COUNT(*) FILTER (WHERE embedding_status = 'complete') as embedded,
    SUM(embedding_chunk_count) as total_chunks
FROM gladiator_documentation;
"

# Generate missing embeddings (follow AYA standard)
cd /Users/arthurdell/AYA/services
python3 -c "
from generate_embeddings_standard import generate_embeddings_for_table
generate_embeddings_for_table(
    table_name='gladiator_documentation',
    project_name='gladiator'
)
"
```

## MISSION STATUS

**Current Objective**: Generate world-class training data (10,000+ high-quality attack-defense pairs)

**Success Criteria**:
- 100% detection rate (✅ ACHIEVED)
- 10M+ attack patterns (in progress)
- <15s response time (✅ ACHIEVED)
- 90% resource reduction (✅ ACHIEVED)

**Next Milestones**:
1. Scale to 10,000 combat sessions
2. Implement advanced persona framework
3. Production hardening
4. Commercial deployment

---

## CRITICAL: AYA-GLADIATOR INTEGRATION

**GLADIATOR is NOT a standalone project.** It is built on top of AYA infrastructure.

### Dependency Stack

```
GLADIATOR (Adversarial AI Cyber Defense)
    ↓ depends on
AYA Infrastructure (Shared Multi-Project RAG System)
    ↓ provides
├─ PostgreSQL Database (aya_rag)
├─ Embedding Service (port 8765, BAAI/bge-base-en-v1.5)
├─ Semantic Search (unified chunks table)
├─ System Monitoring (hardware, software, services)
└─ Documentation Access (10,020+ docs: Docker, PostgreSQL, LM Studio, etc.)
```

### Shared Resources

**Database**: `aya_rag` (38 tables total)
- AYA tables: 20 tables (system monitoring, docs, RAG infrastructure)
- GLADIATOR tables: 11 tables (combat operations, training, validation)
- Shared tables: `chunks` (unified embeddings), `documents` (core registry)

**Services on ALPHA**:
- PostgreSQL 18 (port 5432) - Shared database
- Embedding Service (port 8765) - Shared across all projects
- LM Studio (port 1234) - GLADIATOR Blue Team models

**Services on BETA** (via SSH tunnel):
- LM Studio (port 1234 → ALPHA:1235) - GLADIATOR Red Team models

### Critical Rules

1. **NEVER modify AYA infrastructure tables** without coordination
2. **ALWAYS use embedding service** for any content (MANDATORY standard)
3. **ALWAYS filter by project** when querying shared tables (`metadata->>'project' = 'gladiator'`)
4. **NEVER break embedding standard** (BAAI/bge-base-en-v1.5, 768D vectors)
5. **ALWAYS verify embedding service health** before operations

### Benefits of Shared Infrastructure

**For GLADIATOR**:
- Access to 10,020+ technical docs (Docker, PostgreSQL, MLX, etc.)
- Semantic search across all documentation
- System monitoring and health tracking
- Production-grade PostgreSQL with replication
- Metal-accelerated embedding generation

**For AYA**:
- GLADIATOR provides cybersecurity expertise
- Attack pattern data enhances security knowledge
- Combat validation proves infrastructure scalability
- Cross-project semantic search capabilities

### When Things Break

**If embedding service fails**:
- GLADIATOR documentation can't be embedded
- Combat training data analysis impaired
- Semantic search non-functional

**If database fails**:
- Both AYA and GLADIATOR are down
- No state tracking, no documentation access
- Combat orchestration can't record results

**If replication fails**:
- BETA loses access to shared state
- ALPHA remains operational
- Red Team can still generate attacks (local models)

### Future Projects

This pattern extends to future projects:
- Project 3 adds `project3_*` tables to `aya_rag`
- Project 3 uses same embedding service (port 8765)
- Project 3 chunks stored in same `chunks` table
- Cross-project semantic search: `metadata->>'project' IN ('aya', 'gladiator', 'project3')`

**Scalability**: System designed for 100+ agentic AI agents across multiple projects.

---

*This file is maintained as the canonical source of project structure and development practices for GLADIATOR.*

**Related Documentation**:
- `/Users/arthurdell/AYA/CLAUDE.md` - Prime Directives (source of truth)
- `/Users/arthurdell/AYA/EMBEDDING_STANDARD.md` - MANDATORY embedding protocol
