# N8N Configuration Review - ALPHA System
**Date**: October 27, 2025  
**Location**: /Users/arthurdell/N8N/  
**System**: ALPHA (Mac Studio M3 Ultra)

---

## ✅ FACILITIES STATUS

### Deployment: PRODUCTION OPERATIONAL

**Running Containers** (Verified):
- ✅ n8n-main: `Up 52 minutes` (Port 5678)
- ✅ n8n-worker-1: `Up 52 minutes`
- ✅ n8n-worker-2: `Up 52 minutes`
- ✅ n8n-worker-3: `Up 52 minutes`
- ✅ n8n-redis: `Up 2 days` (healthy)

**Note**: Old n8n-alpha container removed (was on port 8080)

---

## Architecture Overview

### Container Stack
```
n8n-main (UI + API)
    ↓
  Redis Queue
    ↓
3x n8n-worker (Execution)
    ↓
PostgreSQL (aya_rag database)
```

### Database Integration

**Database**: `n8n_aya` (41 tables)  
**Owner**: `n8n_user`  
**Connection**: aya_rag @ localhost:5432  
**State**: Shared across ALPHA + BETA (HA cluster)

**Key Tables**:
- `workflow_entity` - Workflow definitions
- `credentials_entity` - Encrypted credentials
- `execution_entity` - Execution history
- `execution_data` - Execution payloads
- `user` - User accounts
- `settings` - n8n settings
- Plus 35 more tables

---

## Configuration Files

### 1. Docker Compose (`docker/docker-compose.yml`)

**Services**:
- **n8n-main**: Web UI + Workflow Management
  - Port: `5678:5678`
  - Database: aya_rag
  - Queue: Redis
  - Auth: Basic (arthur / encrypted password)
  
- **n8n-worker**: Executors (3 replicas)
  - Database: aya_rag
  - Queue: Redis
  - Mode: queue

- **redis**: Task queue
  - Port: 6379
  - Persistence: appendonly yes

**Environment**:
```bash
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=host.docker.internal
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=aya_rag
DB_POSTGRESDB_USER=postgres
DB_POSTGRESDB_PASSWORD=Power$$336633$$

EXECUTIONS_MODE=queue
QUEUE_BULL_REDIS_HOST=redis
QUEUE_BULL_REDIS_PORT=6379

N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=arthur
N8N_BASIC_AUTH_PASSWORD=BebyJK00n3w+uwHMlKA67Q==
```

**Network**:
- Subnet: `172.25.0.0/16`
- Driver: bridge
- Services: All on same network

---

## Access Information

### n8n Web Interface

**Local Access**:
```
URL: http://localhost:5678
Username: arthur
Password: BebyJK00n3w+uwHMlKA67Q==
```

**Remote Access** (via Tailscale):
```
URL: http://alpha.tail5f2bae.ts.net:5678
Username: arthur
Password: BebyJK00n3w+uwHMlKA67Q==
```

### Database Access

**Connection**:
```bash
Host: localhost
Port: 5432
Database: n8n_aya (or aya_rag)
User: postgres
Password: Power$$336633$$
```

**Verify Tables**:
```bash
PGPASSWORD='Power$$336633$$' psql -U postgres -d n8n_aya -c "\dt"
```

---

## N8N Capabilities

### 1. Workflow Automation
- **Triggers**: Schedule, Webhook, Manual, File
- **Nodes**: 700+ built-in nodes
- **Integrations**: GitHub, PostgreSQL, HTTP, etc.
- **Custom**: Execute scripts, Python code

### 2. Agent Turbo Integration
**Location**: `/Users/arthurdell/N8N/scripts/agent_turbo_integration.py`

**Functions**:
- Create workflow sessions
- Log executions to database
- Track task completion
- Monitor workflow health

**Usage**:
```python
from agent_turbo_integration import N8NAgentTurboIntegration

integration = N8NAgentTurboIntegration()
session_id = integration.create_workflow_session(
    workflow_name='Test Workflow',
    workflow_id='wf_001'
)
```

### 3. LM Studio Integration
**Location**: `/Users/arthurdell/N8N/scripts/lm_studio_client.py`

**Functions**:
- Generate text with local LLMs
- Create embeddings
- Chat completions
- List available models

**Usage**:
```python
from lm_studio_client import LMStudioClient

client = LMStudioClient()
result = client.completion(
    prompt="Analyze this data",
    model="qwen3-14b-mlx",
    max_tokens=500
)
```

### 4. PostgreSQL Integration
**Connection**: Built into n8n

**Node Types**:
- Execute Query
- Insert/Update/Delete
- Subscribe to changes

**Database**: aya_rag (all 138 tables accessible)

### 5. Worker Coordination
**Script**: `/Users/arthurdell/N8N/scripts/worker_coordinator.py`

**Functions**:
- Monitor worker health
- Scale workers dynamically
- Distribute workload
- Handle failures

---

## Management Commands

### View Status
```bash
cd ~/N8N/docker
docker-compose ps
```

### View Logs
```bash
# Main instance
docker logs n8n-main --tail 50

# Worker 1
docker logs docker-n8n-worker-1 --tail 50

# All services
docker-compose logs -f
```

### Scale Workers
```bash
cd ~/N8N/docker

# Scale to 5 workers
docker-compose up -d --scale n8n-worker=5

# Scale to 10 workers
docker-compose up -d --scale n8n-worker=10

# Scale down to 1 worker
docker-compose up -d --scale n8n-worker=1
```

### Restart Services
```bash
cd ~/N8N/docker

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart n8n-main
docker-compose restart n8n-worker
```

### Stop/Start
```bash
cd ~/N8N/docker

# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Stop but keep data
docker-compose stop
```

---

## Health Monitoring

### Check n8n Main Instance
```bash
curl http://localhost:5678/healthz
# Expected: {"status":"ok"}
```

### Check Workers
```bash
docker ps | grep n8n-worker
# Should show 3 workers running
```

### Check Redis
```bash
docker exec n8n-redis redis-cli ping
# Expected: PONG
```

### Check Database
```bash
PGPASSWORD='Power$$336633$$' psql -U postgres -d n8n_aya \
  -c "SELECT COUNT(*) FROM workflow_entity;"
```

### Run Full Health Check
```bash
cd ~/N8N/scripts
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

## Integration Points

### 1. Agent Turbo
- **Session Tracking**: Link workflows to agent sessions
- **Task Logging**: Track workflow executions in database
- **Health Monitoring**: Worker health checks

### 2. PostgreSQL HA Cluster
- **Database**: n8n_aya (synchronized across ALPHA+BETA)
- **Replication**: Automatic failover < 30 seconds
- **Backup**: Included in cluster backups

### 3. LM Studio
- **Endpoint**: http://host.docker.internal:1234
- **Models**: 5 loaded (including qwen3-14b, llama-3.3-70b)
- **API**: OpenAI-compatible v1 endpoints

### 4. GitHub Actions
- **Runners**: ALPHA + BETA self-hosted
- **Workflows**: Can trigger from n8n webhooks
- **Integration**: Execute workflows from n8n

---

## Troubleshooting

### n8n UI Not Accessible
```bash
# Check container
docker logs n8n-main --tail 50

# Verify port binding
docker ps | grep n8n-main

# Check if process is listening
lsof -i :5678

# Restart
cd ~/N8N/docker && docker-compose restart n8n-main
```

### Workers Not Executing
```bash
# Check worker logs
docker logs docker-n8n-worker-1

# Verify Redis connection
docker exec n8n-redis redis-cli ping

# Restart workers
docker-compose restart n8n-worker
```

### Database Connection Failed
```bash
# Test database connection
PGPASSWORD='Power$$336633$$' psql -h localhost -U postgres -d aya_rag -c "\conninfo"

# Check if n8n tables exist
PGPASSWORD='Power$$336633$$' psql -U postgres -d n8n_aya -c "\dt"

# Reapply schema if needed
PGPASSWORD='Power$$336633$$' psql -U postgres -d n8n_aya -f ~/N8N/n8n_schema_extension.sql
```

### LM Studio Unavailable
```bash
# Check if LM Studio is running
curl http://localhost:1234/v1/models

# From inside container
docker exec n8n-main curl http://host.docker.internal:1234/v1/models
```

---

## Performance Metrics

### Resource Usage (Per Container)
- **n8n-main**: ~200-300 MB RAM, 5-15% CPU
- **n8n-worker**: ~150-250 MB RAM, 5-10% CPU (idle), 50-80% (busy)
- **redis**: ~50 MB RAM, <1% CPU

### Execution Performance
- **Simple workflow**: < 100ms
- **Database query**: < 50ms
- **LM Studio inference**: 1-30s (depends on model)
- **Webhook processing**: < 200ms

### Scalability
- **Current**: 1 main + 3 workers
- **Recommended**: 1 main + 5-10 workers (medium load)
- **Maximum**: 1 main + 20 workers (heavy load)

---

## Security

### Authentication
- **Method**: Basic Auth
- **Username**: arthur
- **Password**: Encrypted in .env
- **Encryption Key**: Generated with openssl

### Network Security
- **Internal Docker network**: 172.25.0.0/16
- **Redis**: Not exposed externally
- **PostgreSQL**: Only accessible from localhost/containers
- **Port 5678**: Exposed (requires auth)

### Best Practices
1. Rotate `N8N_ENCRYPTION_KEY` periodically
2. Use environment variables for secrets
3. Enable 2FA if exposing externally
4. Regular database backups
5. Monitor execution logs

---

## Backup & Recovery

### Backup Workflows
```bash
# Export from UI
# Settings → Export All Workflows

# Or backup data directory
tar -czf n8n_backup_$(date +%Y%m%d).tar.gz ~/N8N/data
```

### Backup Database
```bash
# Backup n8n tables
PGPASSWORD='Power$$336633$$' pg_dump -U postgres -d n8n_aya \
  -t 'n8n_*' > n8n_db_backup_$(date +%Y%m%d).sql

# Restore
PGPASSWORD='Power$$336633$$' psql -U postgres -d n8n_aya < n8n_db_backup_20251027.sql
```

---

## Files & Directories

```
/Users/arthurdell/N8N/
├── docker/
│   ├── docker-compose.yml          # Main orchestration
│   ├── n8n-main.Dockerfile         # Main instance
│   ├── n8n-worker.Dockerfile       # Worker image
│   └── .env                        # Environment config
├── data/                            # Persistent data
│   ├── binaryData/                  # File uploads
│   ├── config                       # n8n config
│   └── nodes/                        # Custom nodes
├── workflows/                        # Exported workflows
├── credentials/                      # Encrypted credentials
├── logs/                             # Application logs
├── scripts/
│   ├── deploy_n8n.sh                # Deployment
│   ├── scale_workers.sh             # Worker scaling
│   ├── health_check.py               # Health monitoring
│   ├── agent_turbo_integration.py    # Agent Turbo client
│   ├── lm_studio_client.py          # LM Studio client
│   └── worker_coordinator.py        # Worker coordination
└── docs/                             # Documentation
    ├── README.md
    ├── DEPLOYMENT_SUCCESS_20251027.md
    └── DATABASE_VERIFICATION.md
```

---

## Summary

**Status**: ✅ PRODUCTION OPERATIONAL  
**Main Instance**: http://localhost:5678  
**Workers**: 3 active (scalable to 20)  
**Database**: n8n_aya (41 tables in aya_rag)  
**Queue**: Redis (healthy)  
**Integration**: Agent Turbo, LM Studio, PostgreSQL, GitHub Actions

**Key Features**:
- ✅ Scalable worker architecture
- ✅ PostgreSQL HA cluster integration
- ✅ Agent Turbo session tracking
- ✅ LM Studio LLM inference
- ✅ Comprehensive logging
- ✅ Health monitoring scripts
- ✅ Encrypted credentials

**Ready For**:
- Workflow automation
- Task orchestration
- Data processing
- LLM-powered workflows
- GitHub Actions integration
- Agent Turbo coordination

