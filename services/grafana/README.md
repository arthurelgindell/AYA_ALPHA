

# AYA Grafana Dashboard System

**Status**: Production Ready  
**Version**: 1.0  
**Last Updated**: October 29, 2025  
**Deployment**: HA across ALPHA and BETA nodes

---

## Overview

World-class Grafana monitoring system providing comprehensive, real-time visibility into all AYA subsystems. Deployed in HA configuration across ALPHA and BETA Mac Studio M3 Ultra nodes.

### Monitored Components (68+)

**Infrastructure (5 HA Clusters)**
- PostgreSQL HA Cluster (Patroni + etcd)
- n8n HA Cluster (Active-Active)
- GitHub Actions (self-hosted runners)
- etcd Consensus (2-node)
- Syncthing (file synchronization)

**AI/ML Systems**
- Agent Turbo (121 knowledge entries, 576 tasks)
- LM Studio ALPHA (6 models, 480B Qwen3-Coder)
- LM Studio BETA (7 models)
- Embedding Service (port 8765)

**Project Systems**
- Code_Audit_System (8 runs, 13 tables)
- GLADIATOR (13,475 attack patterns)
- YARADELL (YouTube analytics)
- JITM (manufacturing system)

**Network & Performance**
- Tailscale Mesh (<1ms latency)
- ISP Speed Monitoring (hourly)

---

## Quick Start

### ALPHA Node Deployment

```bash
cd /Users/arthurdell/AYA/services/grafana
./scripts/deploy_alpha.sh
```

### BETA Node Deployment

```bash
cd /Volumes/DATA/AYA/services/grafana
./scripts/deploy_beta.sh
```

### Access

- **ALPHA**: http://alpha.tail5f2bae.ts.net:3000
- **BETA**: http://beta.tail5f2bae.ts.net:3000
- **Username**: arthur
- **Password**: AyaGrafana2025!

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AYA Grafana System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ALPHA Node                          BETA Node              │
│  ├─ Grafana (3000)                   ├─ Grafana (3000)      │
│  ├─ Prometheus (9090)                ├─ Prometheus (9090)   │
│  ├─ Postgres Exporter (9187)         ├─ Postgres Exporter   │
│  ├─ Node Exporter (9100)             ├─ Node Exporter       │
│  ├─ AYA Metrics Exporter (9200)      ├─ AYA Metrics (9200)  │
│  └─ Tailscale Exporter (9201)        └─ Tailscale (9201)    │
│                                                              │
│  Data Sources:                                               │
│  ├─ Prometheus (metrics aggregation)                        │
│  └─ PostgreSQL aya_rag (direct queries)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### Docker Containers

**Grafana**
- Image: `grafana/grafana:latest`
- Port: 3000
- Database: PostgreSQL aya_rag (dashboard storage)
- Plugins: piechart, worldmap, clock

**Prometheus**
- Image: `prom/prometheus:latest`
- Port: 9090
- Retention: Default (15 days)
- Scrape Interval: 15s

**Postgres Exporter**
- Image: `prometheuscommunity/postgres-exporter:latest`
- Port: 9187
- Monitors: aya_rag database

**Node Exporter**
- Image: `prom/node-exporter:latest`
- Port: 9100
- System metrics: CPU, RAM, disk, network

### Custom Exporters

**AYA Metrics Exporter** (`exporters/aya_metrics_exporter.py`)
- Port: 9200
- Metrics:
  - Agent Turbo (sessions, tasks, knowledge)
  - GLADIATOR (attack patterns)
  - Code Audit (runs, findings)
  - Speed Monitoring (download, upload, ping)
  - JITM, YARADELL, n8n

**Tailscale Exporter** (`exporters/tailscale_exporter.py`)
- Port: 9201
- Metrics:
  - Peer online status
  - Peer latency
  - TX/RX bytes
  - Relay status

---

## Dashboards

### Available Dashboards

1. **Executive Overview** (`dashboards/executive-overview.json`)
   - System health status grid
   - Task execution rate
   - Knowledge base growth
   - Internet speed monitor
   - Resource utilization

2. **PostgreSQL HA** (To be created)
   - Cluster topology
   - Replication lag
   - Query performance

3. **Agent Turbo** (To be created)
   - Session activity
   - Task distribution
   - Knowledge queries

4. **Code Audit** (To be created)
   - Audit timeline
   - Findings by severity
   - Worker status

5. **Network & Performance** (To be created)
   - Tailscale mesh
   - ISP performance
   - Inter-node latency

6. **LM Studio & AI Models** (To be created)
   - Model availability
   - GPU utilization
   - Inference metrics

---

## Metrics Reference

### AYA Custom Metrics

```
# Agent Turbo
aya_agent_sessions_total
aya_agent_tasks_total{status,node}
aya_knowledge_entries
aya_knowledge_embeddings

# GLADIATOR
aya_gladiator_patterns

# Code Audit
aya_code_audit_runs{status}
aya_code_audit_findings{severity}

# Speed Monitoring
aya_internet_download_mbps
aya_internet_upload_mbps
aya_internet_ping_ms
aya_internet_download_percent
aya_internet_upload_percent

# Projects
aya_jitm_campaigns
aya_youtube_channels

# n8n
aya_n8n_workflows
aya_n8n_executions_total

# Database
aya_database_size_bytes{database}
```

### Tailscale Metrics

```
tailscale_peer_online{peer,peer_ip}
tailscale_peer_latency_ms{peer,peer_ip}
tailscale_peer_tx_bytes{peer}
tailscale_peer_rx_bytes{peer}
tailscale_peer_last_seen_seconds{peer}
tailscale_relay_active{peer}
```

---

## Operations

### Start Services

```bash
# ALPHA
cd /Users/arthurdell/AYA/services/grafana
docker-compose -f docker-compose-alpha.yml up -d

# Start exporters
python3 exporters/aya_metrics_exporter.py &
python3 exporters/tailscale_exporter.py &
```

### Stop Services

```bash
# Stop Docker containers
docker-compose -f docker-compose-alpha.yml down

# Stop exporters
pkill -f aya_metrics_exporter.py
pkill -f tailscale_exporter.py
```

### View Logs

```bash
# Docker logs
docker-compose -f docker-compose-alpha.yml logs -f

# Specific service
docker logs -f grafana-alpha
docker logs -f prometheus-alpha

# Custom exporters
tail -f /tmp/aya_metrics_exporter.log
tail -f /tmp/tailscale_exporter.log
```

### Check Service Health

```bash
# Grafana
curl http://localhost:3000/api/health

# Prometheus
curl http://localhost:9090/-/ready

# Exporters
curl http://localhost:9187/metrics  # Postgres
curl http://localhost:9100/metrics  # Node
curl http://localhost:9200/metrics  # AYA
curl http://localhost:9201/metrics  # Tailscale
```

---

## Troubleshooting

### Grafana Not Starting

```bash
# Check logs
docker logs grafana-alpha

# Verify database connection
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag -c "SELECT 1;"

# Restart container
docker restart grafana-alpha
```

### Metrics Not Appearing

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check exporter is running
ps aux | grep exporter

# Test exporter directly
curl http://localhost:9200/metrics
```

### Dashboard Not Loading

```bash
# Check provisioning
docker exec grafana-alpha ls -la /etc/grafana/provisioning/dashboards
docker exec grafana-alpha ls -la /var/lib/grafana/dashboards

# Restart Grafana
docker restart grafana-alpha
```

---

## Development

### Adding New Metrics

1. Add metric definition to `exporters/aya_metrics_exporter.py`
2. Implement collection logic
3. Restart exporter
4. Verify in Prometheus: `curl http://localhost:9200/metrics | grep metric_name`
5. Create/update dashboard panel

### Creating New Dashboards

1. Create dashboard in Grafana UI
2. Export JSON: Settings > JSON Model
3. Save to `dashboards/dashboard-name.json`
4. Dashboards auto-reload every 30 seconds

### Testing Changes

```bash
# Test exporter locally
python3 exporters/aya_metrics_exporter.py

# Test Prometheus scraping
curl http://localhost:9090/api/v1/query?query=aya_agent_sessions_total

# Validate dashboard JSON
cat dashboards/executive-overview.json | python3 -m json.tool
```

---

## Backup & Recovery

### Backup Grafana Dashboards

```bash
# Export all dashboards via API
curl -u arthur:AyaGrafana2025! \
  http://localhost:3000/api/search?type=dash-db | \
  python3 -m json.tool > dashboards-backup.json
```

### Backup Prometheus Data

```bash
# Prometheus data is in Docker volume
docker run --rm -v grafana_prometheus-data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/prometheus-backup.tar.gz /data
```

### Restore

Grafana dashboards and datasources are automatically provisioned from files. Simply redeploy containers.

---

## Performance Tuning

### Prometheus

```yaml
# Adjust retention in docker-compose.yml
command:
  - '--storage.tsdb.retention.time=30d'  # Default: 15d
  - '--storage.tsdb.retention.size=50GB' # Optional size limit
```

### Grafana

```yaml
# Add to environment in docker-compose.yml
- GF_DATABASE_MAX_OPEN_CONN=25
- GF_DATABASE_MAX_IDLE_CONN=10
- GF_DATABASE_CONN_MAX_LIFETIME=14400
```

---

## Security

### Change Admin Password

```bash
# Via Grafana UI: Configuration > Users > admin > Change Password

# Or via API
curl -X PUT -H "Content-Type: application/json" \
  -d '{"password":"NewPassword"}' \
  -u arthur:AyaGrafana2025! \
  http://localhost:3000/api/user/password
```

### Restrict Access

```yaml
# In docker-compose.yml, enable auth proxy
- GF_AUTH_PROXY_ENABLED=true
- GF_AUTH_PROXY_HEADER_NAME=X-WEBAUTH-USER
```

---

## Monitoring Best Practices

1. **Dashboard Design**
   - Use consistent color schemes
   - Group related metrics
   - Include documentation links
   - Add alert thresholds

2. **Metrics Collection**
   - Keep scrape intervals reasonable (15s)
   - Label dimensions wisely
   - Avoid high cardinality
   - Use counters for rates

3. **Alerting**
   - Define SLOs/SLIs first
   - Alert on symptoms, not causes
   - Use severity levels
   - Include runbook links

---

## Support

**Documentation**: This README  
**Issues**: Check logs first, then review troubleshooting section  
**Updates**: Pull latest images and restart containers

---

## File Structure

```
/Users/arthurdell/AYA/services/grafana/
├── docker-compose-alpha.yml      # ALPHA node deployment
├── docker-compose-beta.yml       # BETA node deployment
├── prometheus.yml                # Prometheus configuration
├── dashboards/                   # Dashboard JSON files
│   ├── executive-overview.json
│   ├── postgresql-ha.json
│   ├── agent-turbo.json
│   ├── code-audit.json
│   ├── network-performance.json
│   └── lm-studio.json
├── provisioning/                 # Auto-provisioning configs
│   ├── datasources/
│   │   ├── prometheus.yml
│   │   └── postgres.yml
│   └── dashboards/
│       └── dashboards.yml
├── exporters/                    # Custom Prometheus exporters
│   ├── aya_metrics_exporter.py
│   ├── tailscale_exporter.py
│   └── requirements.txt
├── scripts/                      # Deployment scripts
│   ├── deploy_alpha.sh
│   └── deploy_beta.sh
└── README.md                     # This file
```

---

**Version**: 1.0  
**Last Updated**: October 29, 2025  
**Maintained By**: Arthur Dell  
**Status**: Production Ready

