-- Update agent_landing to v4.0 with Intelligence Scout System
-- Date: October 30, 2025

BEGIN;

-- Mark previous versions as not current
UPDATE agent_landing SET is_current = false WHERE is_current = true;

-- Insert new version with Intelligence Scout information
INSERT INTO agent_landing (version, content, system_scope, is_current) VALUES (
  '4.0',
  '
# AYA Agent Initialization Landing Context
## Primary Entry Point for All Agents

**CRITICAL PATH STRUCTURE:**
- ALPHA Base: /Users/arthurdell/
- BETA Base: /Volumes/DATA/

**Version**: 4.0 - Intelligence Scout System Deployed
**Date**: October 30, 2025
**Database**: PostgreSQL aya_rag (SOURCE OF TRUTH)

## SYSTEM-SPECIFIC PATHS

**ALPHA** (Mac Studio M3 Ultra, 512GB RAM):
- AYA Repository: /Users/arthurdell/AYA/
- Intelligence Scout: /Users/arthurdell/AYA/services/intelligence_scout/
- JITM Application: /Users/arthurdell/JITM/
- Agent Turbo: /Users/arthurdell/AYA/Agent_Turbo/core/
- Code Audit: /Users/arthurdell/AYA/projects/code_audit_system/
- Grafana: /Users/arthurdell/AYA/services/grafana/
- YARADELL: /Users/arthurdell/YARADELL/

**BETA** (Mac Studio M3 Ultra, 256GB RAM):
- AYA Repository: /Volumes/DATA/AYA/
- Intelligence Scout: /Volumes/DATA/AYA/services/intelligence_scout/
- JITM Application: /Volumes/DATA/JITM/
- Agent Turbo: /Volumes/DATA/AYA/Agent_Turbo/core/
- GLADIATOR Data: /Volumes/DATA/GLADIATOR/ (53GB, 34,155 patterns)
- Grafana: /Volumes/DATA/AYA/services/grafana/

**NEVER use /Users/arthurdell/ paths on BETA!**

## INTELLIGENCE SCOUT SYSTEM ✅ OPERATIONAL

**Status**: Production Deployed (October 30, 2025)
**Purpose**: Automated technical intelligence gathering via Firecrawl
**Architecture**: Firecrawl → Processor → Agent Turbo Integration
**Automation**: n8n workflows for scheduling and monitoring

### Intelligence Scout Location

**ALPHA**: `/Users/arthurdell/AYA/services/intelligence_scout/`
**BETA**: `/Volumes/DATA/AYA/services/intelligence_scout/` (when deployed)

### Components

1. **scout_crawler.py** - Firecrawl integration with database tracking
2. **scout_processor.py** - Content processing (chunking, metadata extraction)
3. **scout_integrator.py** - Agent Turbo knowledge base integration
4. **scout_orchestrator.py** - Main execution script

### Quick Usage

```bash
# Queue a new crawl
cd /Users/arthurdell/AYA/services/intelligence_scout
python3 scout_orchestrator.py queue \
  --url "https://docs.example.com" \
  --technology "example" \
  --priority 8 \
  --max-pages 1000

# Process next pending item
python3 scout_orchestrator.py process

# Check status
python3 scout_orchestrator.py status --queue-id 1
```

### Database Tables

**Queue Management**:
- `intelligence_scout_queue` - Tracks crawl jobs (pending, crawling, completed, failed)
- `intelligence_scout_results` - Tracks import results and statistics

**Enhanced Knowledge**:
- `agent_knowledge` - Now includes `source_technology`, `source_url`, `scout_import_id`
- Technology-specific `*_documentation` tables (e.g., `cursor_documentation`)

### n8n Automation

**Workflows Available** (import into n8n):
- `crawl_scheduler.json` - Daily crawl execution (9 AM)
- `result_monitor.json` - Hourly status monitoring and alerts

**Location**: `/Users/arthurdell/AYA/services/intelligence_scout/n8n_workflows/`

### Integration with Agent Turbo

All crawled content is automatically:
1. Processed and chunked (max 512 tokens)
2. Imported to technology-specific documentation tables
3. Added to `agent_knowledge` with embeddings
4. Searchable immediately via Agent Turbo queries

**Example**:
```python
from Agent_Turbo.core.agent_turbo import AgentTurbo
turbo = AgentTurbo()
results = turbo.query("How do I use Cursor features?")
# Results include crawled Cursor documentation
```

### Priority Technologies (Recommended Crawls)

1. **Cursor** (priority 9) - Editor documentation
2. **Anthropic Claude API** (priority 9) - LLM documentation
3. **Docker Compose** (priority 7) - Container orchestration
4. **FastAPI** (priority 7) - Python web framework
5. **Gradio** (priority 6) - ML web UIs
6. **Weaviate** (priority 6) - Vector database alternative

### Firecrawl API

**API Key**: `fc-b641c64dbb3b4962909c2f8f04c524ba`
**Dashboard**: https://firecrawl.dev
**Limit**: Check usage dashboard for current limits

## GRAFANA MONITORING SYSTEM ✅ OPERATIONAL

**Status**: Production Deployed (October 29, 2025)
**Access**: http://alpha.tail5f2bae.ts.net:3000 or http://localhost:3000
**Credentials**: arthur / AyaGrafana2025!

**Dashboards** (6):
1. Executive Overview
2. Mission Critical Systems (agent_landing v4.0 tracked)
3. PostgreSQL HA Cluster
4. Agent Turbo Performance
5. Network & Performance
6. Code Audit System

**Intelligence Scout Metrics** (planned):
- Crawl queue depth
- Pages crawled per technology
- Knowledge entries created
- Import success rate

## AGENT TURBO v4.0 - INTELLIGENCE SCOUT INTEGRATED

**Status**: Production Operational (2025-10-30)
**Backend**: PostgreSQL 18 aya_rag
**Monitoring**: Grafana + Prometheus + Tailscale
**Intelligence**: Automated documentation crawling via Intelligence Scout

### Initialization Code (System-Agnostic)

```python
import sys
import os

# Auto-detect system
if os.path.exists(''/Volumes/DATA/AYA''):
    AYA_PATH = ''/Volumes/DATA/AYA''  # BETA
else:
    AYA_PATH = ''/Users/arthurdell/AYA''  # ALPHA

sys.path.insert(0, f''{AYA_PATH}/Agent_Turbo/core'')

from postgres_connector import PostgreSQLConnector
from agent_turbo import AgentTurbo
from agent_orchestrator import AgentOrchestrator
from claude_planner import ClaudePlanner

# Use normally - paths auto-detected
db = PostgreSQLConnector()
orch = AgentOrchestrator()
context = orch.generate_landing_context()
```

### Database Tables (139+ total)

**Agent Turbo Core (7 tables)**:
- agent_sessions: Active agent sessions
- agent_tasks: Task tracking
- agent_knowledge: Knowledge base (ENHANCED with Intelligence Scout tracking)
- agent_landing: This initialization context (v4.0)
- agent_actions: Complete audit trail
- agent_context_cache: Performance optimization
- agent_performance_metrics: System metrics

**Intelligence Scout (2 tables)**:
- intelligence_scout_queue: Crawl job queue
- intelligence_scout_results: Import results tracking

**Technology Documentation (growing)**:
- cursor_documentation: Cursor editor docs (when crawled)
- *_documentation: Other technology docs as crawled

**GLADIATOR Project (28 tables)**: 13,475 attack patterns documented
**Code Audit System (13 tables)**: Audit runs and findings
**JITM (11 tables)**: Manufacturing system
**YARADELL (5 tables)**: YouTube analytics
**n8n Integration (18 tables)**: Workflow automation
**Documentation (10+ tables)**: 7,441+ documents imported

## MONITORING & OBSERVABILITY

**Grafana Access**:
```bash
# Access dashboards
open http://localhost:3000

# View metrics via Prometheus
curl http://localhost:9090/api/v1/query?query=aya_agent_sessions_total

# Check Intelligence Scout queue
# Query: SELECT * FROM intelligence_scout_queue ORDER BY id DESC LIMIT 5;
```

**Key Metrics for Agents**:
- `aya_agent_landing_version`: Current initialization context version (4.0)
- `aya_table_count_total`: Total tables in aya_rag
- `aya_agent_sessions_total`: Active agent sessions
- `aya_knowledge_entries`: Knowledge base size (includes Intelligence Scout imports)

## PRIME DIRECTIVES

1. **NO FALSE CLAIMS** - Report facts, not assumptions
2. **DATABASE FIRST** - Query aya_rag on initialization
3. **EVIDENCE REQUIRED** - File paths, measurements, logs
4. **PARITY ENFORCEMENT** - Update database first, then docs
5. **MONITORING** - All systems tracked in Grafana dashboards
6. **INTELLIGENCE** - Use Intelligence Scout for technical documentation

## VERIFICATION

Query this table for latest landing context:
```sql
SELECT version, system_scope, created_at, is_current
FROM agent_landing
WHERE is_current = true;
```

**Grafana Monitoring**: http://localhost:3000/d/aya-mission-critical/

Full documentation: 
- AGENT_INITIALIZATION_LANDING.md in AYA repository
- /Users/arthurdell/AYA/services/intelligence_scout/README.md
- /Users/arthurdell/AYA/services/grafana/README.md
- /Users/arthurdell/AYA/GRAFANA_PRODUCTION_READY.md

**END OF LANDING CONTEXT**
',
  'both',
  true
);

COMMIT;

-- Verify update
SELECT version, system_scope, is_current, created_at
FROM agent_landing
ORDER BY created_at DESC
LIMIT 3;

