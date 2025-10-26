# PostgreSQL Schema Files
**Organized**: 2025-10-26  
**Database**: aya_rag (PostgreSQL 18)

All schema definition and migration files for the AYA PostgreSQL database.

## Schema Files

### Core Infrastructure
**aya_schema_implementation.sql**
- Core AYA infrastructure tables
- 11 tables: system_nodes, active_services, change_log, etc.
- Created: 2025-10-09
- Status: Deployed in production

### Agent Turbo v2.0
**migrate_agent_turbo_schema.sql**
- Agent orchestration system tables  
- 6 tables: agent_sessions, agent_tasks, agent_knowledge, agent_actions, etc.
- Features: pgvector embeddings, full audit trail
- Created: 2025-10-26
- Status: Deployed and operational

### n8n Workflow Automation
**n8n_schema_extension.sql**
- n8n workflow system extensions
- Integration with aya_rag database
- Created: 2025-10-25
- Status: Deployed with n8n HA cluster

## JITM Schema

JITM schema (10 tables) is deployed but not tracked in separate file.

Query existing tables:
```sql
\dt jitm_*
```

## Usage

### Apply Schema
```bash
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql \
  -U postgres -d aya_rag -f services/schemas/[schema_file].sql
```

### Verify Deployment
```bash
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql \
  -U postgres -d aya_rag -c "\dt"
```

## Current Database

**aya_rag**: 583 MB, 120 tables
- 6 agent_* tables (Agent Turbo)
- 10 jitm_* tables (JITM)
- 41 n8n_* tables (n8n HA)
- 11 infrastructure tables
- Multiple GLADIATOR tables
- Documentation and knowledge tables

