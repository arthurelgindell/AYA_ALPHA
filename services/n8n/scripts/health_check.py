#!/usr/bin/env python3
"""
n8n Infrastructure Health Check
Verifies all components are operational with actual connectivity tests
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

import requests
import psycopg2
from datetime import datetime, timedelta
import subprocess


def check_n8n_api():
    """Check if n8n main instance is responding"""
    try:
        response = requests.get('http://localhost:5678/healthz', timeout=5)
        return response.status_code == 200
    except:
        return False


def check_n8n_ui():
    """Check if n8n UI is accessible"""
    try:
        response = requests.get('http://localhost:5678', timeout=5)
        return response.status_code in [200, 401]  # 401 is expected with auth
    except:
        return False


def check_redis():
    """Check if Redis is responding"""
    try:
        result = subprocess.run(
            ['docker', 'exec', 'n8n-redis', 'redis-cli', 'ping'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'PONG' in result.stdout
    except:
        return False


def check_database_connection():
    """Check PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='aya_rag',
            user='postgres',
            password='Power$$336633$$',
            connect_timeout=5
        )
        conn.close()
        return True
    except:
        return False


def check_database_schema():
    """Verify n8n tables exist"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='aya_rag',
            user='postgres',
            password='Power$$336633$$'
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('n8n_workflows', 'n8n_executions', 'n8n_workers')
        """)
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return count == 3
    except:
        return False


def check_workers():
    """Check worker status from database"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='aya_rag',
            user='postgres',
            password='Power$$336633$$'
        )
        cur = conn.cursor()
        
        # Get workers with recent heartbeats
        cur.execute("""
            SELECT worker_id, status, last_heartbeat,
                   NOW() - last_heartbeat as time_since_heartbeat
            FROM n8n_workers 
            WHERE last_heartbeat > NOW() - INTERVAL '10 minutes'
            ORDER BY last_heartbeat DESC
        """)
        
        workers = cur.fetchall()
        cur.close()
        conn.close()
        
        return len(workers), workers
    except:
        return 0, []


def check_docker_containers():
    """Check Docker containers status"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=n8n', '--format', '{{.Names}}:{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                name, status = line.split(':', 1)
                containers.append((name, 'Up' in status))
        
        return containers
    except:
        return []


def check_lm_studio():
    """Check if LM Studio is accessible"""
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json().get('data', [])
            return True, len(models)
        return False, 0
    except:
        return False, 0


def get_execution_stats():
    """Get workflow execution statistics"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='aya_rag',
            user='postgres',
            password='Power$$336633$$'
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_executions,
                SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as failed,
                AVG(execution_time_ms) as avg_time_ms
            FROM n8n_executions
            WHERE started_at > NOW() - INTERVAL '24 hours'
        """)
        
        stats = cur.fetchone()
        cur.close()
        conn.close()
        
        return stats
    except:
        return None


def main():
    """Run comprehensive health check"""
    print("=" * 60)
    print("N8N INFRASTRUCTURE HEALTH CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_healthy = True
    
    # Check n8n API
    print("n8n Main Instance:")
    api_status = check_n8n_api()
    ui_status = check_n8n_ui()
    print(f"  API Health:    {'✅ OPERATIONAL' if api_status else '❌ DOWN'}")
    print(f"  UI Access:     {'✅ ACCESSIBLE' if ui_status else '❌ UNAVAILABLE'}")
    if not (api_status and ui_status):
        all_healthy = False
    
    # Check Redis
    print("\nRedis Queue:")
    redis_status = check_redis()
    print(f"  Status:        {'✅ OPERATIONAL' if redis_status else '❌ DOWN'}")
    if not redis_status:
        all_healthy = False
    
    # Check Database
    print("\nDatabase (aya_rag):")
    db_conn = check_database_connection()
    db_schema = check_database_schema()
    print(f"  Connection:    {'✅ CONNECTED' if db_conn else '❌ DISCONNECTED'}")
    print(f"  Schema:        {'✅ VERIFIED' if db_schema else '❌ MISSING TABLES'}")
    if not (db_conn and db_schema):
        all_healthy = False
    
    # Check Workers
    print("\nWorkers:")
    worker_count, workers = check_workers()
    if worker_count > 0:
        print(f"  Active:        ✅ {worker_count} workers")
        for worker in workers[:5]:  # Show max 5
            time_diff = worker[3] if len(worker) > 3 else None
            age = f"({time_diff})" if time_diff else ""
            print(f"    - {worker[0]}: {worker[1]} {age}")
    else:
        print(f"  Active:        ⚠️  NO WORKERS REGISTERED")
        print(f"    Note: Workers may need time to register")
    
    # Check Docker Containers
    print("\nDocker Containers:")
    containers = check_docker_containers()
    if containers:
        for name, is_up in containers:
            status_icon = "✅" if is_up else "❌"
            status_text = "Up" if is_up else "Down"
            print(f"  {name}: {status_icon} {status_text}")
            if not is_up:
                all_healthy = False
    else:
        print(f"  Status:        ❌ NO CONTAINERS FOUND")
        all_healthy = False
    
    # Check LM Studio
    print("\nLM Studio Integration:")
    lm_available, model_count = check_lm_studio()
    print(f"  Status:        {'✅ AVAILABLE' if lm_available else '⚠️  UNAVAILABLE'}")
    if lm_available:
        print(f"  Models:        {model_count} loaded")
    
    # Execution Statistics
    print("\nExecution Statistics (24h):")
    stats = get_execution_stats()
    if stats and stats[0] is not None:
        total, successful, failed, avg_time = stats
        success_rate = (successful / total * 100) if total > 0 else 0
        print(f"  Total:         {int(total)}")
        print(f"  Successful:    {int(successful)}")
        print(f"  Failed:        {int(failed)}")
        print(f"  Success Rate:  {success_rate:.1f}%")
        if avg_time:
            print(f"  Avg Time:      {int(avg_time)}ms")
    else:
        print(f"  No executions in last 24 hours")
    
    # Overall Status
    print()
    print("=" * 60)
    if all_healthy:
        print("OVERALL STATUS: ✅ ALL SYSTEMS OPERATIONAL")
    else:
        print("OVERALL STATUS: ⚠️  SOME SYSTEMS NEED ATTENTION")
    print("=" * 60)
    
    return 0 if all_healthy else 1


if __name__ == '__main__':
    sys.exit(main())

