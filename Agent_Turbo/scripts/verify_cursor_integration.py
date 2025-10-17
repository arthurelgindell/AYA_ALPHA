#!/usr/bin/env python3
"""
Verify Agent Turbo integration with Cursor
"""

import os
import sys
import json
from pathlib import Path

def check_status_file():
    """Check if Agent Turbo service is running."""
    status_file = Path.home() / '.cursor' / 'agent_turbo_status.json'
    
    if not status_file.exists():
        return False, "Status file not found"
    
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        if status.get('status') != 'active':
            return False, f"Service status: {status.get('status')}"
        
        return True, status
    except Exception as e:
        return False, f"Error reading status: {e}"

def check_tasks_json():
    """Check if Cursor tasks are configured."""
    tasks_file = Path('/Volumes/DATA/Agent_Turbo/.vscode/tasks.json')
    
    if not tasks_file.exists():
        return False, "tasks.json not found"
    
    try:
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        task_count = len(tasks.get('tasks', []))
        auto_run_tasks = [t for t in tasks.get('tasks', []) 
                         if t.get('runOptions', {}).get('runOn') == 'folderOpen']
        
        return True, {
            'total_tasks': task_count,
            'auto_run_tasks': len(auto_run_tasks),
            'task_labels': [t.get('label') for t in tasks.get('tasks', [])]
        }
    except Exception as e:
        return False, f"Error reading tasks: {e}"

def check_agent_turbo():
    """Check if Agent Turbo is directly accessible."""
    sys.path.insert(0, '/Volumes/DATA/Agent_Turbo')
    
    try:
        from core.agent_turbo import AgentTurbo
        turbo = AgentTurbo()
        
        verified = turbo.verify()
        stats = json.loads(turbo.stats())
        
        return verified, stats
    except Exception as e:
        return False, f"Error initializing Agent Turbo: {e}"

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("AGENT_TURBO CURSOR INTEGRATION VERIFICATION")
    print("=" * 60)
    
    # Check 1: Agent Turbo Core
    print("\n[1] Checking Agent Turbo Core...")
    verified, result = check_agent_turbo()
    if verified:
        print("    ✅ Agent Turbo is operational")
        print(f"    📊 Entries: {result.get('entries')}")
        print(f"    🚀 GPU: {result.get('using_gpu')}")
        print(f"    💾 Memory: {result.get('memory_used_mb'):.1f} MB")
    else:
        print(f"    ❌ Agent Turbo failed: {result}")
        return False
    
    # Check 2: Cursor Tasks Configuration
    print("\n[2] Checking Cursor Tasks Configuration...")
    configured, result = check_tasks_json()
    if configured:
        print("    ✅ Cursor tasks configured")
        print(f"    📋 Total tasks: {result.get('total_tasks')}")
        print(f"    🚀 Auto-run tasks: {result.get('auto_run_tasks')}")
        for label in result.get('task_labels', []):
            print(f"       - {label}")
    else:
        print(f"    ❌ Tasks configuration failed: {result}")
        return False
    
    # Check 3: Service Status
    print("\n[3] Checking Background Service Status...")
    running, result = check_status_file()
    if running and isinstance(result, dict):
        print("    ✅ Background service is running")
        print(f"    🆔 PID: {result.get('pid')}")
        print(f"    📁 Workspace: {result.get('workspace')}")
        print(f"    🕐 Last update: {result.get('timestamp')}")
        if 'stats' in result:
            print(f"    📊 Service stats available: {len(result['stats'])} metrics")
    else:
        print(f"    ⚠️  Background service not running: {result}")
        print("    ℹ️  Service will start when Cursor opens the workspace")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 60)
    print("\nAgent Turbo is ready for use with Cursor.")
    print("\nTo activate:")
    print("  1. Close and reopen this workspace in Cursor")
    print("  2. Agent Turbo will auto-start via tasks.json")
    print("  3. Use 'Agent Turbo: Verify Status' task to check")
    print("\n" + "=" * 60)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

