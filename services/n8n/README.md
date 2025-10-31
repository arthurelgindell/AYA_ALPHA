# N8N Production Infrastructure
**AI Workflow Automation with Scalable Worker Architecture**

## Overview

Production-grade n8n deployment integrated with AYA infrastructure:
- **Main Instance**: Web UI + workflow management
- **Worker Pool**: 3-20 scalable workers for execution
- **Database**: PostgreSQL aya_rag (Agent Turbo integrated)
- **Queue**: Redis for distributed task coordination
- **Integration**: LM Studio + Agent Turbo + PostgreSQL

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AYA INFRASTRUCTURE                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌────────────┐    ┌────────────┐  │
│  │  PostgreSQL  │◄───│  n8n Main  │───►│   Redis    │  │
│  │   aya_rag    │    │  Instance  │    │   Queue    │  │
│  │  (Port 5432) │    │ (Port 5678)│    │ (Port 6379)│  │
│  └──────────────┘    └────────────┘    └────────────┘  │
│         ▲                   │                   ▲        │
│         │                   │                   │        │
│         │            ┌──────┴──────┐            │        │
│         │            │             │            │        │
│         │      ┌─────▼────┐  ┌────▼─────┐      │        │
│         └──────│ Worker 1 │  │ Worker 2 │──────┘        │
│                └──────────┘  └──────────┘                │
│                      │              │                     │
│                      ▼              ▼                     │
│               ┌────────────────────────┐                 │
│               │    LM Studio API       │                 │
│               │   (localhost:1234)     │                 │
│               └────────────────────────┘                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Deploy Infrastructure

```bash
cd /Users/arthurdell/N8N/scripts
./deploy_n8n.sh
```

This will:
- Verify directory structure
- Apply database schema
- Generate encryption keys
- Build Docker images
- Start all services (main + 3 workers + Redis)
- Run health checks

### 2. Access n8n UI

```
URL:      http://localhost:5678
Username: arthur
Password: (see /Users/arthurdell/N8N/docker/.env)
```

### 3. Verify Deployment

```bash
cd /Users/arthurdell/N8N/scripts
python3 health_check.py
```

Expected output:
```
N8N INFRASTRUCTURE HEALTH CHECK
================================
n8n Main Instance:  ✅ OPERATIONAL
Redis Queue:        ✅ OPERATIONAL
Database (aya_rag): ✅ CONNECTED
Workers:            ✅ 3 active
```

---

## Operations

### Scale Workers

```bash
# Scale to 5 workers
/Users/arthurdell/N8N/scripts/scale_workers.sh 5

# Scale to 10 workers
/Users/arthurdell/N8N/scripts/scale_workers.sh 10

# Scale down to 1 worker
/Users/arthurdell/N8N/scripts/scale_workers.sh 1
```

### Monitor Status

```bash
# Full health check
python3 /Users/arthurdell/N8N/scripts/health_check.py

# Docker containers
cd /Users/arthurdell/N8N/docker
docker-compose ps

# Logs
docker-compose logs -f n8n-main      # Main instance
docker-compose logs -f n8n-worker    # All workers
docker-compose logs -f redis         # Redis queue
```

### Restart Services

```bash
cd /Users/arthurdell/N8N/docker

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart n8n-main
docker-compose restart n8n-worker
docker-compose restart redis
```

### Stop/Start

```bash
cd /Users/arthurdell/N8N/docker

# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Stop but keep data
docker-compose stop
```

---

## Agent Turbo Integration

### Creating Workflow Sessions

Use Agent Turbo integration to track workflows:

```python
from agent_turbo_integration import N8NAgentTurboIntegration

integration = N8NAgentTurboIntegration()

# Create session for workflow
session_id = integration.create_workflow_session(
    workflow_name='Data Processing Pipeline',
    workflow_id='wf_001'
)

# Log execution
integration.log_workflow_execution(
    workflow_id='wf_001',
    execution_id='exec_12345',
    status='running',
    metadata={'input': 'data.csv'}
)

# Mark complete
integration.update_execution_complete(
    execution_id='exec_12345',
    success=True,
    execution_time_ms=2500
)
```

### Query from n8n Workflows

Use **Execute Command** or **HTTP Request** nodes:

```javascript
// Query database from n8n
const { exec } = require('child_process');

exec('python3 /home/node/.n8n/agent_turbo_integration.py', (error, stdout) => {
  if (error) {
    console.error('Error:', error);
    return;
  }
  console.log('Output:', stdout);
});
```

---

## LM Studio Integration

### Available Models

Check loaded models:

```bash
curl http://localhost:1234/v1/models
```

### Using LM Studio Client

```python
from lm_studio_client import LMStudioClient

client = LMStudioClient()

# Simple completion
result = client.completion(
    prompt="Analyze this security log: ...",
    model="foundation-sec-8b-instruct-int8",
    max_tokens=500
)

# Chat completion
result = client.chat_completion(
    messages=[
        {'role': 'system', 'content': 'You are a security analyst.'},
        {'role': 'user', 'content': 'Explain this vulnerability.'}
    ],
    model="qwen3-next-80b-a3b-instruct-mlx"
)

# Generate embeddings
result = client.embedding(
    text="Document to embed",
    model="text-embedding-nomic-embed-text-v1.5"
)
```

### From n8n HTTP Request Node

```json
{
  "method": "POST",
  "url": "http://host.docker.internal:1234/v1/completions",
  "body": {
    "model": "foundation-sec-8b-instruct-int8",
    "prompt": "{{$json.prompt}}",
    "max_tokens": 500,
    "temperature": 0.7
  },
  "headers": {
    "Content-Type": "application/json"
  }
}
```

**Note**: Use `host.docker.internal` from inside Docker containers to access ALPHA services.

---

## Database Schema

### n8n_workflows
Tracks all workflow definitions:

```sql
SELECT * FROM n8n_workflows WHERE status = 'active';
```

Columns:
- `workflow_id`: Unique workflow identifier
- `workflow_name`: Human-readable name
- `agent_session_id`: Linked Agent Turbo session
- `metadata`: Workflow configuration (JSONB)

### n8n_executions
Logs all workflow executions:

```sql
SELECT * FROM n8n_executions 
WHERE started_at > NOW() - INTERVAL '24 hours'
ORDER BY started_at DESC;
```

Columns:
- `execution_id`: Unique execution identifier
- `workflow_id`: Parent workflow
- `success`: Boolean success/failure
- `execution_time_ms`: Duration
- `error_message`: Error details if failed

### n8n_workers
Tracks worker health:

```sql
SELECT * FROM n8n_worker_health;
```

View returns:
- `worker_id`: Container name
- `health_status`: healthy/warning/stale
- `last_heartbeat`: Last check-in time

---

## Workflow Patterns

### Pattern 1: Database Query → LLM Analysis → Store Result

1. **PostgreSQL** node: Query aya_rag
2. **HTTP Request** node: Send to LM Studio
3. **PostgreSQL** node: Store analysis

### Pattern 2: Scheduled Data Processing

1. **Schedule Trigger**: Every hour
2. **Execute Command**: Run Python script
3. **Condition**: Check results
4. **HTTP Request**: Notify via webhook

### Pattern 3: Webhook → Agent Turbo Task

1. **Webhook** node: Receive request
2. **Execute Command**: Create Agent Turbo task
3. **Wait**: Poll for completion
4. **Return**: Send response

---

## Troubleshooting

### n8n UI Not Accessible

```bash
# Check main container
docker logs n8n-main --tail 50

# Verify port binding
docker ps | grep n8n-main

# Check if process is listening
lsof -i :5678
```

### Workers Not Executing

```bash
# Check worker logs
docker-compose logs n8n-worker

# Verify Redis connection
docker exec n8n-redis redis-cli ping

# Check worker registration
psql -U postgres -d aya_rag -c "SELECT * FROM n8n_workers;"
```

### Database Connection Failed

```bash
# Test database connection
PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -c "\conninfo"

# Check if tables exist
psql -U postgres -d aya_rag -c "\dt n8n_*"

# Reapply schema if needed
psql -U postgres -d aya_rag -f /Users/arthurdell/AYA/n8n_schema_extension.sql
```

### LM Studio Unavailable

```bash
# Check if LM Studio is running
curl http://localhost:1234/v1/models

# From inside container
docker exec n8n-main curl http://host.docker.internal:1234/v1/models
```

---

## File Structure

```
/Users/arthurdell/N8N/
├── docker/
│   ├── docker-compose.yml      # Main orchestration
│   ├── n8n-main.Dockerfile     # Main instance image
│   ├── n8n-worker.Dockerfile   # Worker image
│   └── .env                     # Environment config
├── workflows/                   # Exported workflows (JSON)
├── credentials/                 # Encrypted credentials
├── data/                        # n8n persistent data
├── logs/                        # Application logs
└── scripts/
    ├── deploy_n8n.sh            # Main deployment script
    ├── scale_workers.sh         # Worker scaling
    ├── health_check.py          # Health monitoring
    ├── agent_turbo_integration.py  # Agent Turbo client
    ├── lm_studio_client.py      # LM Studio client
    └── worker_coordinator.py    # Worker coordination
```

---

## Performance

### Recommended Worker Counts

- **Light workloads**: 3 workers (default)
- **Medium workloads**: 5-10 workers
- **Heavy workloads**: 10-20 workers

### Resource Usage (Per Worker)

- **RAM**: ~200-300 MB
- **CPU**: ~5-10% idle, 50-80% during execution
- **Network**: Minimal (queue-based)

### Monitoring Metrics

```sql
-- Execution statistics
SELECT 
    DATE(started_at) as date,
    COUNT(*) as executions,
    AVG(execution_time_ms) as avg_time_ms,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as success_rate
FROM n8n_executions
GROUP BY DATE(started_at)
ORDER BY date DESC
LIMIT 7;
```

---

## Security

### Credentials Storage

- Stored encrypted in `/Users/arthurdell/N8N/credentials/`
- Encryption key in `.env` (keep secure)
- **Never commit `.env` to git**

### Network Security

- n8n UI requires basic auth (username: arthur)
- Internal Docker network isolated (172.20.0.0/16)
- PostgreSQL only accessible from localhost
- Redis not exposed externally

### Best Practices

1. Rotate `N8N_ENCRYPTION_KEY` periodically
2. Use environment variables for secrets
3. Enable 2FA if exposing externally
4. Regular database backups
5. Monitor execution logs for anomalies

---

## Backup & Recovery

### Backup Workflows

```bash
# Export all workflows (from n8n UI)
# Settings → Export All Workflows

# Or backup data directory
tar -czf n8n_backup_$(date +%Y%m%d).tar.gz /Users/arthurdell/N8N/data
```

### Backup Database

```bash
# Backup n8n tables
pg_dump -U postgres -d aya_rag -t 'n8n_*' > n8n_db_backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres -d aya_rag < n8n_db_backup_20251025.sql
```

---

## Support

### Documentation
- n8n Official: https://docs.n8n.io/
- Agent Turbo: `/Users/arthurdell/AYA/Agent_Turbo/AGENT_INTEGRATION_GUIDE.md`
- This README: `/Users/arthurdell/N8N/README.md`

### Logs
- n8n Main: `docker-compose logs n8n-main`
- Workers: `docker-compose logs n8n-worker`
- Redis: `docker-compose logs redis`
- System: `/Users/arthurdell/N8N/logs/`

### Health Check
```bash
python3 /Users/arthurdell/N8N/scripts/health_check.py
```

---

## Version Information

- **n8n**: latest (via n8nio/n8n:latest)
- **Redis**: 7-alpine
- **PostgreSQL**: 18.0 (aya_rag)
- **Python**: 3.x (in containers)
- **Deployment Date**: October 25, 2025
- **System**: ALPHA (Mac Studio M3 Ultra)

---

**Status**: Production Ready ✅  
**Deployed**: /Users/arthurdell/N8N/  
**Database**: aya_rag @ localhost:5432  
**UI**: http://localhost:5678

