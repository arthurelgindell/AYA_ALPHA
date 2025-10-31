#!/usr/bin/env python3
"""
AYA Metrics Exporter for Prometheus
Exposes AYA-specific metrics from aya_rag database and speed_monitoring
"""
import psycopg2
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import sys
import os

# Define metrics
agent_sessions_total = Gauge('aya_agent_sessions_total', 'Total agent sessions')
agent_tasks_total = Gauge('aya_agent_tasks_total', 'Total agent tasks', ['status', 'node'])
agent_knowledge_entries = Gauge('aya_knowledge_entries', 'Knowledge base entries')
agent_knowledge_with_embeddings = Gauge('aya_knowledge_embeddings', 'Knowledge entries with embeddings')
gladiator_patterns_total = Gauge('aya_gladiator_patterns', 'GLADIATOR attack patterns')
code_audit_runs_total = Gauge('aya_code_audit_runs', 'Code audit runs', ['status'])
code_audit_findings = Gauge('aya_code_audit_findings', 'Code audit findings', ['severity'])
speed_monitoring_download = Gauge('aya_internet_download_mbps', 'Internet download speed Mbps')
speed_monitoring_upload = Gauge('aya_internet_upload_mbps', 'Internet upload speed Mbps')
speed_monitoring_ping = Gauge('aya_internet_ping_ms', 'Internet ping latency ms')
speed_monitoring_percent_download = Gauge('aya_internet_download_percent', 'Download speed as % of plan')
speed_monitoring_percent_upload = Gauge('aya_internet_upload_percent', 'Upload speed as % of plan')
jitm_campaigns = Gauge('aya_jitm_campaigns', 'JITM campaigns count')
youtube_channels = Gauge('aya_youtube_channels', 'YouTube channels monitored')
n8n_workflows = Gauge('aya_n8n_workflows', 'N8N workflow count')
n8n_executions_total = Counter('aya_n8n_executions_total', 'N8N total executions')
database_size_bytes = Gauge('aya_database_size_bytes', 'Database size in bytes', ['database'])
agent_landing_version = Gauge('aya_agent_landing_version', 'Agent Landing version info', ['version', 'system_scope', 'is_current'])
agent_landing_age_seconds = Gauge('aya_agent_landing_age_seconds', 'Seconds since agent_landing was updated')
table_count_total = Gauge('aya_table_count_total', 'Total tables in aya_rag database')
agent_turbo_tables = Gauge('aya_agent_turbo_tables', 'Agent Turbo table info', ['table_name'])

def collect_metrics():
    """Collect metrics from PostgreSQL aya_rag database"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='aya_rag',
            user='postgres',
            password='Power$$336633$$'
        )
        cur = conn.cursor()
        
        # Agent sessions
        cur.execute("SELECT COUNT(*) FROM agent_sessions")
        agent_sessions_total.set(cur.fetchone()[0])
        
        # Agent tasks by status and platform
        cur.execute("""
            SELECT 
                COALESCE(status, 'unknown') as status,
                COALESCE(assigned_to_platform, 'unassigned') as node,
                COUNT(*) 
            FROM agent_tasks 
            GROUP BY status, assigned_to_platform
        """)
        for status, node, count in cur.fetchall():
            agent_tasks_total.labels(status=status, node=node).set(count)
        
        # Knowledge entries
        cur.execute("SELECT COUNT(*) FROM agent_knowledge")
        agent_knowledge_entries.set(cur.fetchone()[0])
        
        # Knowledge with embeddings
        cur.execute("SELECT COUNT(*) FROM agent_knowledge WHERE embedding IS NOT NULL")
        agent_knowledge_with_embeddings.set(cur.fetchone()[0])
        
        # GLADIATOR patterns
        cur.execute("SELECT COUNT(*) FROM gladiator_attack_patterns")
        gladiator_patterns_total.set(cur.fetchone()[0])
        
        # Code audit runs by status
        cur.execute("SELECT status, COUNT(*) FROM code_audit_runs GROUP BY status")
        for status, count in cur.fetchall():
            code_audit_runs_total.labels(status=status).set(count)
        
        # Code audit findings by severity
        try:
            cur.execute("""
                SELECT severity, COUNT(*) 
                FROM code_audit_findings 
                WHERE status = 'open'
                GROUP BY severity
            """)
            for severity, count in cur.fetchall():
                code_audit_findings.labels(severity=severity).set(count)
        except:
            pass  # Table may not exist yet
        
        # JITM campaigns
        cur.execute("SELECT COUNT(*) FROM jitm_campaigns")
        jitm_campaigns.set(cur.fetchone()[0])
        
        # YouTube channels
        cur.execute("SELECT COUNT(*) FROM youtube_channels")
        youtube_channels.set(cur.fetchone()[0])
        
        # N8N workflows from n8n_aya database
        try:
            cur.execute("SELECT COUNT(*) FROM workflow_entity")
            n8n_workflows.set(cur.fetchone()[0])
            
            cur.execute("SELECT COUNT(*) FROM execution_entity")
            n8n_executions_total._value.set(cur.fetchone()[0])
        except:
            pass  # May not have access to n8n_aya
        
        # Database sizes
        cur.execute("""
            SELECT 
                datname, 
                pg_database_size(datname) as size 
            FROM pg_database 
            WHERE datname IN ('aya_rag', 'n8n_aya')
        """)
        for dbname, size in cur.fetchall():
            database_size_bytes.labels(database=dbname).set(size)
        
        # Agent Landing (MISSION CRITICAL)
        try:
            cur.execute("""
                SELECT version, system_scope, is_current, 
                       EXTRACT(EPOCH FROM (NOW() - updated_at)) as age_seconds
                FROM agent_landing 
                WHERE is_current = true
            """)
            row = cur.fetchone()
            if row:
                version, scope, is_current, age = row
                agent_landing_version.labels(version=version, system_scope=scope, is_current=str(is_current)).set(1)
                agent_landing_age_seconds.set(age)
        except Exception as e:
            print(f"Error collecting agent_landing metrics: {e}", file=sys.stderr)
        
        # Table count
        try:
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
            table_count_total.set(cur.fetchone()[0])
        except Exception as e:
            print(f"Error collecting table count: {e}", file=sys.stderr)
        
        # Agent Turbo table sizes
        try:
            cur.execute("""
                SELECT tablename, pg_total_relation_size('public.'||tablename) 
                FROM pg_tables 
                WHERE schemaname='public' AND tablename LIKE 'agent_%'
            """)
            for table_name, size in cur.fetchall():
                agent_turbo_tables.labels(table_name=table_name).set(size)
        except Exception as e:
            print(f"Error collecting agent table sizes: {e}", file=sys.stderr)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error collecting database metrics: {e}", file=sys.stderr)

def collect_speed_monitoring():
    """Parse latest speed monitoring data from CSV"""
    try:
        speed_file = '/Users/arthurdell/speed_monitoring/speed_data.csv'
        if not os.path.exists(speed_file):
            return
            
        with open(speed_file, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                latest = lines[-1].strip().split(',')
                if len(latest) >= 10:
                    # CSV format: timestamp,date,time,hour,ping_ms,download_mbps,upload_mbps,download_percent,upload_percent,server
                    try:
                        ping = float(latest[4]) if latest[4] and latest[4] != ':' and latest[4] != 'ERROR' else 0
                    except ValueError:
                        ping = 0
                    
                    try:
                        download = float(latest[5]) if latest[5] and latest[5] != 'ERROR' else 0
                    except ValueError:
                        download = 0
                    
                    try:
                        upload = float(latest[6]) if latest[6] and latest[6] != 'ERROR' else 0
                    except ValueError:
                        upload = 0
                    
                    try:
                        download_pct = float(latest[7]) if latest[7] and latest[7] != 'ERROR' else 0
                    except ValueError:
                        download_pct = 0
                    
                    try:
                        upload_pct = float(latest[8]) if latest[8] and latest[8] != 'ERROR' else 0
                    except ValueError:
                        upload_pct = 0
                    
                    speed_monitoring_ping.set(ping)
                    speed_monitoring_download.set(download)
                    speed_monitoring_upload.set(upload)
                    speed_monitoring_percent_download.set(download_pct)
                    speed_monitoring_percent_upload.set(upload_pct)
    except Exception as e:
        print(f"Error reading speed monitoring: {e}", file=sys.stderr)

if __name__ == '__main__':
    print("Starting AYA Metrics Exporter on port 9200...")
    start_http_server(9200)  # Expose metrics on port 9200
    print("AYA Metrics Exporter running. Metrics available at http://localhost:9200/metrics")
    
    while True:
        try:
            collect_metrics()
            collect_speed_monitoring()
        except Exception as e:
            print(f"Error in collection loop: {e}", file=sys.stderr)
        time.sleep(15)  # Collect every 15 seconds

