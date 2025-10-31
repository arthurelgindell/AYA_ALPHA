# Intelligence Scout System

**Automated Technical Intelligence Gathering System**

## Overview

Intelligence Scout automatically crawls documentation sites, processes content, and integrates it into AYA's knowledge base via Agent Turbo. The system is designed for maximum automation via n8n workflows.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   n8n Workflow  │────▶│  Firecrawl   │────▶│ Process/Format  │
│  (Scheduling)   │     │   Crawler    │     │    Pipeline     │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
                        ┌──────────────────────────────▼────────┐
                        │         PostgreSQL aya_rag            │
                        ├────────────────────────────────────────┤
                        │ • intelligence_scout_queue             │
                        │ • intelligence_scout_results           │
                        │ • agent_knowledge (enhanced)            │
                        │ • *_documentation tables                │
                        └────────────────────────────────────────┘
                                          │
                                    ┌─────▼──────┐
                                    │Agent Turbo │
                                    │ Knowledge  │
                                    │Integration │
                                    └────────────┘
```

## Components

### 1. scout_crawler.py
Enhanced Firecrawl integration with database progress tracking.

**Features:**
- Firecrawl API integration
- Queue-based crawling
- Progress tracking in PostgreSQL
- Automatic retry on failure

### 2. scout_processor.py
Content processing pipeline for knowledge ingestion.

**Features:**
- Markdown cleaning and normalization
- Intelligent chunking (max 512 tokens)
- Metadata extraction (version, category, importance)
- Deduplication against existing knowledge

### 3. scout_integrator.py
Agent Turbo knowledge base integration.

**Features:**
- Creates technology-specific documentation tables
- Imports to agent_knowledge with embeddings
- Source tracking (technology, URL, import ID)
- Batch processing for performance

### 4. scout_orchestrator.py
Main execution script coordinating all components.

**Usage:**
```bash
# Queue a new crawl
python3 scout_orchestrator.py queue \
  --url "https://docs.example.com" \
  --technology "example" \
  --priority 8 \
  --max-pages 1000

# Process next pending item
python3 scout_orchestrator.py process

# Process specific queue ID
python3 scout_orchestrator.py process --queue-id 1

# Check status
python3 scout_orchestrator.py status --queue-id 1
```

## Database Schema

### intelligence_scout_queue
Tracks crawl jobs:
- `id`: Queue ID
- `url`: URL to crawl
- `technology_name`: Technology identifier
- `priority`: 1-10 (higher = more important)
- `max_pages`: Maximum pages to crawl
- `status`: pending, queued, crawling, processing, completed, failed
- `crawl_id`: Firecrawl crawl ID
- `pages_crawled`: Progress counter

### intelligence_scout_results
Tracks import results:
- `id`: Result ID
- `queue_id`: Reference to queue item
- `technology_name`: Technology identifier
- `table_name`: Documentation table created
- `pages_imported`: Number of pages imported
- `words_total`: Total words processed
- `embeddings_generated`: Number of knowledge entries
- `knowledge_ids`: Array of agent_knowledge IDs

### agent_knowledge (Enhanced)
Now includes:
- `source_technology`: Technology name
- `source_url`: Source URL with chunk anchor
- `scout_import_id`: Reference to intelligence_scout_results

## n8n Workflows

### 1. Crawl Scheduler (`crawl_scheduler.json`)
- **Trigger**: Daily at 9 AM
- **Action**: Queries queue for pending items, executes highest priority crawl
- **Location**: `/Users/arthurdell/AYA/services/intelligence_scout/n8n_workflows/`

### 2. Result Monitor (`result_monitor.json`)
- **Trigger**: Hourly
- **Action**: Checks recent results, sends status reports, alerts on failures
- **Location**: `/Users/arthurdell/AYA/services/intelligence_scout/n8n_workflows/`

**To import workflows:**
1. Open n8n at http://localhost:5678
2. Go to Workflows → Import from File
3. Select the JSON files from `n8n_workflows/`
4. Configure credentials (PostgreSQL, SSH, SMTP)
5. Activate workflows

## Quick Start

### 1. Queue a Crawl

```bash
cd /Users/arthurdell/AYA/services/intelligence_scout
python3 scout_orchestrator.py queue \
  --url "https://docs.cursor.com" \
  --technology "cursor" \
  --priority 8 \
  --max-pages 500
```

### 2. Process Queue

```bash
python3 scout_orchestrator.py process
```

This will:
1. Get next pending item from queue
2. Start Firecrawl crawl
3. Monitor progress
4. Process documents (chunk, extract metadata)
5. Import to documentation table
6. Import chunks to agent_knowledge
7. Record results
8. Update queue status

### 3. Check Status

```bash
# Check queue
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag \
  -c "SELECT * FROM intelligence_scout_queue ORDER BY id DESC LIMIT 5;"

# Check results
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag \
  -c "SELECT * FROM intelligence_scout_results ORDER BY import_timestamp DESC LIMIT 5;"
```

## Priority Technologies

Recommended initial crawl targets:

1. **Cursor** (priority 9) - Editor we're using
2. **Anthropic Claude API** (priority 9) - LLM documentation
3. **Docker Compose** (priority 7) - Container orchestration
4. **FastAPI** (priority 7) - Python web framework
5. **Gradio** (priority 6) - ML web UIs
6. **Weaviate** (priority 6) - Vector database alternative

## Integration with Agent Turbo

All imported content is immediately searchable via Agent Turbo:

```python
from Agent_Turbo.core.agent_turbo import AgentTurbo

turbo = AgentTurbo()
results = turbo.query("How do I use Cursor's AI features?")
# Results include crawled Cursor documentation
```

## Troubleshooting

### Crawl Fails
Check queue error_message:
```sql
SELECT id, technology_name, error_message, status 
FROM intelligence_scout_queue 
WHERE status = 'failed' 
ORDER BY completed_at DESC;
```

### No Embeddings Generated
Verify embedding service is running:
```bash
curl http://localhost:8765/health
```

### Firecrawl API Limits
Current API key: `fc-b641c64dbb3b4962909c2f8f04c524ba`
Check usage at https://firecrawl.dev

## Files

- `scout_crawler.py` - Firecrawl integration
- `scout_processor.py` - Content processing
- `scout_integrator.py` - Agent Turbo integration
- `scout_orchestrator.py` - Main execution script
- `schema.sql` - Database schema
- `n8n_workflows/` - n8n workflow definitions

## Status

✅ Core modules implemented
✅ Database schema deployed
✅ n8n workflows designed
⏳ Testing with Cursor documentation
⏳ Agent landing update pending

---

**Created**: October 30, 2025  
**Version**: 1.0  
**Maintainer**: Arthur Dell

