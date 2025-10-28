#!/usr/bin/env python3
"""
Test script for parallel execution MVP
Creates sample tasks and monitors execution
"""

import sys
import os
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from postgres_connector import PostgreSQLConnector

def create_test_tasks(db: PostgreSQLConnector, num_tasks: int = 3):
    """Create test tasks in database"""
    print(f"\n🔄 Creating {num_tasks} test tasks...")
    
    tasks_created = []
    
    for i in range(num_tasks):
        task_id = f"test_task_{uuid.uuid4().hex[:8]}"
        
        # Different test scenarios
        if i == 0:
            description = "List the files in the current directory and count them"
        elif i == 1:
            description = "Calculate the sum of numbers from 1 to 100 and show the result"
        else:
            description = f"Echo back: 'Test task #{i+1} - parallel execution working'"
        
        query = """
            INSERT INTO agent_tasks (
                task_id,
                task_type,
                task_description,
                task_priority,
                status,
                timeout_seconds,
                max_retries,
                retry_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        db.execute_query(
            query,
            (task_id, 'test', description, 5, 'pending', 60, 3, 0)
        )
        
        tasks_created.append(task_id)
        print(f"  ✅ Created: {task_id} - {description[:50]}...")
    
    return tasks_created


def monitor_tasks(db: PostgreSQLConnector, task_ids: list, timeout: int = 120):
    """Monitor task execution"""
    print(f"\n👀 Monitoring task execution (timeout: {timeout}s)...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        query = """
            SELECT 
                task_id,
                status,
                assigned_worker_id,
                started_at,
                completed_at,
                error_message
            FROM agent_tasks
            WHERE task_id = ANY(%s)
            ORDER BY created_at
        """
        
        results = db.execute_query(query, (task_ids,), fetch=True)
        
        # Clear screen (simple version)
        print("\n" + "=" * 70)
        print(f"⏱️  Elapsed: {int(time.time() - start_time)}s")
        print("=" * 70)
        
        pending_count = 0
        running_count = 0
        completed_count = 0
        failed_count = 0
        
        for task in results:
            status_icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(task['status'], '❓')
            
            print(f"{status_icon} {task['task_id']}: {task['status'].upper()}")
            
            if task['assigned_worker_id']:
                print(f"   Worker: {task['assigned_worker_id']}")
            
            if task['started_at']:
                print(f"   Started: {task['started_at']}")
            
            if task['completed_at']:
                duration = (task['completed_at'] - task['started_at']).total_seconds()
                print(f"   Duration: {duration:.1f}s")
            
            if task['error_message']:
                print(f"   Error: {task['error_message'][:100]}")
            
            # Count statuses
            if task['status'] == 'pending':
                pending_count += 1
            elif task['status'] == 'running':
                running_count += 1
            elif task['status'] == 'completed':
                completed_count += 1
            elif task['status'] == 'failed':
                failed_count += 1
        
        print("\n" + "-" * 70)
        print(f"📊 Summary: Pending={pending_count}, Running={running_count}, " +
              f"Completed={completed_count}, Failed={failed_count}")
        print("=" * 70)
        
        # Check if all tasks complete
        if pending_count == 0 and running_count == 0:
            print(f"\n✅ All tasks finished!")
            print(f"   Completed: {completed_count}")
            print(f"   Failed: {failed_count}")
            return True
        
        time.sleep(2)
    
    print(f"\n⏱️  Timeout reached after {timeout}s")
    return False


def show_task_results(db: PostgreSQLConnector, task_ids: list):
    """Show task outputs"""
    print(f"\n📋 Task Results:")
    print("=" * 70)
    
    query = """
        SELECT 
            task_id,
            task_description,
            status,
            output_data,
            error_message
        FROM agent_tasks
        WHERE task_id = ANY(%s)
        ORDER BY completed_at
    """
    
    results = db.execute_query(query, (task_ids,), fetch=True)
    
    for task in results:
        print(f"\n🔹 {task['task_id']}")
        print(f"   Description: {task['task_description'][:80]}...")
        print(f"   Status: {task['status'].upper()}")
        
        if task['status'] == 'completed' and task['output_data']:
            output = task['output_data'].get('output', 'No output')
            print(f"   Output: {output[:200]}...")
        elif task['error_message']:
            print(f"   Error: {task['error_message']}")
        
        print("-" * 70)


def main():
    """Main test flow"""
    print("=" * 70)
    print("  PARALLEL EXECUTION MVP TEST")
    print("=" * 70)
    
    # Connect to database
    print("\n🔌 Connecting to database...")
    db = PostgreSQLConnector()
    print("✅ Connected")
    
    # Create test tasks
    task_ids = create_test_tasks(db, num_tasks=3)
    
    print(f"\n✅ {len(task_ids)} tasks created")
    print("\n⚠️  NOW START THE WORKER IN ANOTHER TERMINAL:")
    print("   cd /Users/arthurdell/AYA/Agent_Turbo/core")
    print("   python3 task_worker.py")
    print("\nPress Enter when worker is running...")
    input()
    
    # Monitor execution
    success = monitor_tasks(db, task_ids, timeout=120)
    
    if success:
        # Show results
        show_task_results(db, task_ids)
        
        print("\n" + "=" * 70)
        print("  ✅ MVP TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  TEST TIMEOUT - CHECK WORKER LOGS")
        print("=" * 70)
    
    db.close()


if __name__ == "__main__":
    main()

