#!/usr/bin/env python3
"""
AIR Utility Script
Purpose: Provide AIR node with easy access to operational context and monitoring tools
Single Source of Truth: PostgreSQL aya_rag database
"""

import sys
import json
import subprocess
import os
from typing import Dict, List, Optional

# Database configuration
DB_CONFIG = {
    'host': 'alpha.tail5f2bae.ts.net',
    'port': 5432,
    'database': 'aya_rag',
    'user': 'postgres',
    'password': os.getenv('PGPASSWORD', 'Power$$336633$$')
}

def run_command(cmd: str, shell: bool = True) -> Optional[str]:
    """Execute shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print(f"Command failed: {e}", file=sys.stderr)
        return None

def query_database(sql: str) -> Optional[str]:
    """Execute PostgreSQL query and return results."""
    cmd = f"PGPASSWORD='{DB_CONFIG['password']}' psql -h {DB_CONFIG['host']} -U {DB_CONFIG['user']} -d {DB_CONFIG['database']} -c \"{sql}\""
    return run_command(cmd)

def get_operational_context() -> Dict:
    """Retrieve AIR operational context from database."""
    sql = "SELECT * FROM node_operational_contexts WHERE node_name='AIR';"
    cmd = f"PGPASSWORD='{DB_CONFIG['password']}' psql -h {DB_CONFIG['host']} -U {DB_CONFIG['user']} -d {DB_CONFIG['database']} -t -c \"{sql}\""
    output = run_command(cmd)

    if not output:
        return {'error': 'Failed to retrieve operational context'}

    # Parse the output (simplified - assumes single row)
    return {'raw': output}

def check_cluster_health() -> Dict:
    """Check Patroni cluster health."""
    cmd = "curl -s http://alpha.tail5f2bae.ts.net:8008/cluster"
    output = run_command(cmd)

    if not output:
        return {'status': 'unreachable', 'error': 'Cannot connect to Patroni API'}

    try:
        cluster = json.loads(output)
        return {
            'status': 'healthy',
            'scope': cluster.get('scope'),
            'members': [
                {
                    'name': m.get('name'),
                    'role': m.get('role'),
                    'state': m.get('state'),
                    'lag': m.get('lag', 'N/A')
                }
                for m in cluster.get('members', [])
            ]
        }
    except json.JSONDecodeError:
        return {'status': 'error', 'error': 'Invalid JSON response'}

def check_workers() -> Dict:
    """Check Agent Turbo workers on ALPHA and BETA."""
    alpha_cmd = "ssh alpha.tail5f2bae.ts.net 'ps aux | grep task_worker.py | wc -l'"
    beta_cmd = "ssh beta.tail5f2bae.ts.net 'ps aux | grep task_worker.py | wc -l'"

    alpha_workers = run_command(alpha_cmd)
    beta_workers = run_command(beta_cmd)

    return {
        'alpha': {
            'workers': max(0, int(alpha_workers) - 1) if alpha_workers else 0,  # Prevent negative count
            'expected': 10
        },
        'beta': {
            'workers': max(0, int(beta_workers) - 1) if beta_workers else 0,  # Prevent negative count
            'expected': 10
        }
    }

def check_task_distribution() -> Dict:
    """Check task distribution across nodes."""
    sql = """
        SELECT
          CASE
            WHEN assigned_worker_id LIKE '%alpha%' THEN 'ALPHA'
            WHEN assigned_worker_id LIKE '%beta%' THEN 'BETA'
            ELSE 'UNKNOWN'
          END as node,
          status,
          COUNT(*) as count
        FROM agent_tasks
        WHERE created_at > NOW() - INTERVAL '1 hour'
        GROUP BY 1, 2
        ORDER BY 1, 2;
    """

    output = query_database(sql)
    return {'raw': output if output else 'No data'}

def check_system_nodes() -> Dict:
    """Check system nodes from database."""
    sql = """
        SELECT node_name, node_role, ram_gb, storage_internal_tb,
               COALESCE(storage_external_tb, 0) as storage_external_tb,
               metadata->>'working_path' as working_path, status
        FROM system_nodes
        ORDER BY node_name;
    """

    output = query_database(sql)
    return {'raw': output if output else 'No data'}

def check_database_stats() -> Dict:
    """Check database statistics."""
    sql = """
        SELECT
            pg_size_pretty(pg_database_size('aya_rag')) as database_size,
            (SELECT COUNT(*) FROM agent_sessions) as total_sessions,
            (SELECT COUNT(*) FROM agent_tasks) as total_tasks,
            (SELECT COUNT(*) FROM agent_knowledge) as knowledge_entries;
    """

    output = query_database(sql)
    return {'raw': output if output else 'No data'}

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("AIR Utility Script")
        print("Usage: python3 air_utility.py <command>")
        print("")
        print("Commands:")
        print("  context          - Retrieve AIR operational context from database")
        print("  cluster          - Check Patroni cluster health")
        print("  workers          - Check Agent Turbo workers on ALPHA/BETA")
        print("  tasks            - Check task distribution across nodes")
        print("  nodes            - Check system nodes from database")
        print("  dbstats          - Check database statistics")
        print("  status           - Full system status check")
        print("")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'context':
        context = get_operational_context()
        print(json.dumps(context, indent=2))

    elif command == 'cluster':
        health = check_cluster_health()
        print(json.dumps(health, indent=2))

    elif command == 'workers':
        workers = check_workers()
        print(json.dumps(workers, indent=2))

    elif command == 'tasks':
        tasks = check_task_distribution()
        print(json.dumps(tasks, indent=2))

    elif command == 'nodes':
        nodes = check_system_nodes()
        print(json.dumps(nodes, indent=2))

    elif command == 'dbstats':
        stats = check_database_stats()
        print(json.dumps(stats, indent=2))

    elif command == 'status':
        print("=== AIR SYSTEM STATUS ===\n")

        print("Cluster Health:")
        health = check_cluster_health()
        if health['status'] == 'healthy':
            for member in health.get('members', []):
                role_icon = '👑' if member['role'] == 'leader' else '🔄'
                print(f"  {role_icon} {member['name']}: {member['role']} ({member['state']}) - Lag: {member['lag']}")
        else:
            print(f"  ⚠️  {health.get('error', 'Unknown error')}")

        print("\nAgent Turbo Workers:")
        workers = check_workers()
        alpha_status = '✓' if workers['alpha']['workers'] >= 8 else '⚠️'
        beta_status = '✓' if workers['beta']['workers'] >= 5 else '⚠️'
        print(f"  {alpha_status} ALPHA: {workers['alpha']['workers']}/{workers['alpha']['expected']} workers")
        print(f"  {beta_status} BETA: {workers['beta']['workers']}/{workers['beta']['expected']} workers")

        print("\nSystem Nodes:")
        nodes_output = query_database("SELECT node_name, node_role, status FROM system_nodes ORDER BY node_name;")
        if nodes_output:
            print(nodes_output)

        print("\nDatabase Stats:")
        stats_output = query_database("SELECT pg_size_pretty(pg_database_size('aya_rag')) as size, (SELECT COUNT(*) FROM agent_tasks WHERE created_at > NOW() - INTERVAL '1 hour') as recent_tasks;")
        if stats_output:
            print(stats_output)

        print("\n=== END STATUS ===")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
