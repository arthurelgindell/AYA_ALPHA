# N8N Workflow Setup Guide

## Prerequisites

- n8n instance running at http://localhost:5678
- YouTube API credentials configured in `/Users/arthurdell/YARADELL/config/.env`
- Scripts tested and functional

## Workflow 1: Daily Audience Snapshot

**Trigger**: Schedule - Every day at 6:00 AM  
**Purpose**: Collect daily audience demographics and behavior data

### Nodes Configuration

```
1. Schedule Trigger
   - Cron: 0 6 * * *
   - Timezone: America/Los_Angeles

2. Set Variables
   - Name: config_paths
   - Values:
     - SCRIPT_PATH: /Users/arthurdell/YARADELL/scripts/youtube_api_client.py
     - ENV_PATH: /Users/arthurdell/YARADELL/config/.env

3. Execute Command: Fetch Channel Info
   - Command: python3
   - Args: {{$node["Set Variables"].json["SCRIPT_PATH"]}}
   - Working Directory: /Users/arthurdell/YARADELL/scripts

4. PostgreSQL: Log Session
   - Operation: Insert
   - Table: agent_sessions
   - Columns:
     - session_id: youtube_daily_{{$now.toFormat('yyyyMMdd_HHmmss')}}
     - agent_type: 'youtube_collector'
     - landing_context: 'Daily audience data collection'

5. IF: Check Success
   - Condition: {{$json["exitCode"]}} == 0

6. PostgreSQL: Update Stats
   - IF True Branch
   - Operation: Execute Query
   - Query: UPDATE youtube_channels SET updated_at = NOW()

7. Set Success Message
   - Name: log_success
   - Values:
     - status: 'success'
     - message: 'Daily snapshot completed'
     - timestamp: {{$now}}

8. (Optional) Send Notification
   - Webhook or email notification on failure
```

## Workflow 2: Weekly Deep Analysis

**Trigger**: Schedule - Every Monday at 7:00 AM  
**Purpose**: Generate AI insights and comprehensive reports

### Nodes Configuration

```
1. Schedule Trigger
   - Cron: 0 7 * * 1
   - Timezone: America/Los_Angeles

2. PostgreSQL: Fetch Week Data
   - Operation: Execute Query
   - Query: |
     SELECT 
       channel_id, 
       COUNT(*) as snapshots
     FROM youtube_audience_demographics
     WHERE snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
     GROUP BY channel_id

3. Execute Command: Run Analysis
   - Command: python3
   - Args: /Users/arthurdell/YARADELL/scripts/audience_analyzer.py
   - Working Directory: /Users/arthurdell/YARADELL/scripts

4. Execute Command: Generate Reports
   - Command: python3
   - Args: /Users/arthurdell/YARADELL/scripts/report_generator.py
   - Working Directory: /Users/arthurdell/YARADELL/scripts

5. PostgreSQL: Log Insights
   - Operation: Insert
   - Table: youtube_insights_log
   - Data from previous node output

6. HTTP Request: Update Dashboard
   - Method: POST
   - URL: http://localhost:8080/api/refresh
   - (Triggers dashboard data reload)

7. Set Success Message
   - Name: weekly_complete
   - Values:
     - status: 'success'
     - report_generated: true
     - insights_saved: true
```

## Manual Import Instructions

### Option A: Manual Creation (Recommended for Learning)

1. Open n8n: http://localhost:5678
2. Click "+ New Workflow"
3. Add nodes as specified above
4. Configure each node with the settings
5. Test each node individually
6. Save and activate workflow

### Option B: JSON Import (Advanced)

1. Copy the workflow JSON from below
2. In n8n, click "Import from File" or "Import from URL"
3. Paste the JSON
4. Update any environment-specific paths
5. Save and activate

## Testing Workflows

### Test Daily Snapshot

```bash
# From n8n UI, click "Execute Workflow" manually
# OR trigger via cron:
# 1. Wait for 6:00 AM
# 2. Check logs in n8n UI
# 3. Verify data in database:

PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -c "
SELECT snapshot_date, age_18_24_percent, engagement_rate 
FROM youtube_audience_demographics 
ORDER BY snapshot_date DESC 
LIMIT 5;
"
```

### Test Weekly Analysis

```bash
# Manually trigger from n8n UI
# Check reports generated:
ls -lh /Users/arthurdell/YARADELL/reports/

# Check insights in database:
PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -c "
SELECT insight_date, summary, confidence_score 
FROM youtube_insights_log 
ORDER BY insight_date DESC 
LIMIT 3;
"
```

## Monitoring

### Check Workflow Execution History

1. Open n8n UI: http://localhost:5678
2. Navigate to "Executions" tab
3. View success/failure status
4. Inspect execution data and logs

### Database Monitoring

```bash
# Check latest snapshots
PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -h localhost -c "
SELECT 
  'demographics' as table_name, 
  MAX(snapshot_date) as latest_date,
  COUNT(*) as total_rows
FROM youtube_audience_demographics
UNION ALL
SELECT 
  'behavior',
  MAX(snapshot_date),
  COUNT(*)
FROM youtube_audience_behavior
UNION ALL
SELECT 
  'insights',
  MAX(insight_date)::date,
  COUNT(*)
FROM youtube_insights_log;
"
```

## Troubleshooting

### Workflow Not Triggering

**Check**:
1. Workflow is activated (green toggle in n8n)
2. n8n container is running: `docker ps | grep n8n`
3. System time is correct: `date`

### Python Script Errors

**Check**:
1. Scripts have execute permissions: `ls -l /Users/arthurdell/YARADELL/scripts/`
2. Python dependencies installed: `pip3 list | grep google-api`
3. Environment variables set: `cat /Users/arthurdell/YARADELL/config/.env`

### Database Connection Issues

**Check**:
1. PostgreSQL credentials in n8n match .env file
2. `pg_hba.conf` allows connections from n8n
3. Test connection: `PGPASSWORD='...' psql -U postgres -h localhost -d aya_rag -c "SELECT 1;"`

## Integration with Agent Turbo

All workflow executions are tracked in Agent Turbo:

- **Sessions**: `agent_sessions` table
- **Tasks**: `agent_tasks` table  
- **n8n Executions**: `n8n_executions` table

Query execution history:
```sql
SELECT 
  s.session_id,
  s.agent_type,
  s.created_at,
  COUNT(t.task_id) as tasks_completed
FROM agent_sessions s
LEFT JOIN agent_tasks t ON s.session_id = t.session_id
WHERE s.agent_type LIKE 'youtube%'
GROUP BY s.session_id, s.agent_type, s.created_at
ORDER BY s.created_at DESC
LIMIT 10;
```

## Next Steps

1. ✅ Configure YouTube API credentials
2. ✅ Test scripts individually
3. ✅ Create workflows in n8n UI
4. ✅ Test manual execution
5. ✅ Activate automated schedules
6. ✅ Monitor first week of data collection
7. ✅ Review generated reports
8. ✅ Refine based on insights

---

**Last Updated**: 2025-10-25

