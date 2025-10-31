#!/usr/bin/env python3
"""
Setup N8N Automation for Intelligence Scout
Imports failsafe workflows and configures automation
"""

import json
import os
import sys
import requests
from pathlib import Path

# N8N Configuration
N8N_API_URL = os.getenv('N8N_API_URL', 'http://localhost:5678')
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

if not N8N_API_KEY:
    # Try to load from .env in mcp_servers/n8n-mcp
    env_file = Path(__file__).parent.parent.parent / 'mcp_servers' / 'n8n-mcp' / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith('N8N_API_KEY='):
                    N8N_API_KEY = line.split('=', 1)[1].strip()
                    break
                elif line.startswith('N8N_API_URL='):
                    N8N_API_URL = line.split('=', 1)[1].strip()

if not N8N_API_KEY:
    print("❌ N8N_API_KEY not found. Please set in environment or .env file")
    sys.exit(1)

HEADERS = {
    'X-N8N-API-KEY': N8N_API_KEY,
    'Content-Type': 'application/json'
}

def check_n8n_health():
    """Check if N8N is accessible"""
    try:
        response = requests.get(f"{N8N_API_URL}/api/v1/health", headers=HEADERS, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  N8N health check failed: {e}")
        return False

def list_existing_workflows():
    """List existing workflows to check for duplicates"""
    try:
        response = requests.get(f"{N8N_API_URL}/api/v1/workflows", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"⚠️  Failed to list workflows: {e}")
        return []

def create_workflow(workflow_data):
    """Create/import workflow in N8N"""
    try:
        # Remove workflow ID if present (n8n will assign new one)
        if 'id' in workflow_data:
            del workflow_data['id']
        
        # Ensure workflow is not active initially
        workflow_data['active'] = False
        
        response = requests.post(
            f"{N8N_API_URL}/api/v1/workflows",
            headers=HEADERS,
            json=workflow_data,
            timeout=30
        )
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            workflow_id = result.get('id') or result.get('data', {}).get('id')
            return {'success': True, 'workflow_id': workflow_id, 'data': result}
        else:
            return {'success': False, 'error': f"Status {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def activate_workflow(workflow_id):
    """Activate a workflow"""
    try:
        response = requests.post(
            f"{N8N_API_URL}/api/v1/workflows/{workflow_id}/activate",
            headers=HEADERS,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Failed to activate workflow {workflow_id}: {e}")
        return False

def main():
    """Main execution"""
    print("🚀 N8N Automation Setup for Intelligence Scout")
    print("=" * 60)
    
    # Check N8N health
    print("\n1️⃣ Checking N8N health...")
    if not check_n8n_health():
        print("❌ N8N is not accessible. Please ensure N8N is running.")
        print(f"   Expected URL: {N8N_API_URL}")
        sys.exit(1)
    print("✅ N8N is accessible")
    
    # List existing workflows
    print("\n2️⃣ Checking existing workflows...")
    existing = list_existing_workflows()
    existing_names = {w.get('name') for w in existing}
    print(f"   Found {len(existing)} existing workflows")
    
    # Load workflow files
    workflows_dir = Path(__file__).parent / 'n8n_workflows'
    
    workflows_to_import = [
        ('crawl_scheduler_failsafe.json', 'Intelligence Scout - Failsafe Crawl Scheduler'),
        ('result_monitor.json', 'Intelligence Scout - Result Monitor'),
    ]
    
    imported = []
    skipped = []
    failed = []
    
    print("\n3️⃣ Importing workflows...")
    for filename, expected_name in workflows_to_import:
        filepath = workflows_dir / filename
        
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            failed.append((filename, "File not found"))
            continue
        
        # Check if already exists
        if expected_name in existing_names:
            print(f"⏭️  Skipping {filename} (workflow '{expected_name}' already exists)")
            skipped.append((filename, expected_name))
            continue
        
        # Load and import
        print(f"📥 Importing {filename}...")
        try:
            with open(filepath) as f:
                workflow_data = json.load(f)
            
            result = create_workflow(workflow_data)
            
            if result['success']:
                workflow_id = result['workflow_id']
                print(f"   ✅ Created workflow ID: {workflow_id}")
                
                # Activate workflow
                if activate_workflow(workflow_id):
                    print(f"   ✅ Activated workflow")
                else:
                    print(f"   ⚠️  Workflow created but not activated")
                
                imported.append((filename, workflow_id))
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                failed.append((filename, result.get('error', 'Unknown error')))
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed.append((filename, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 IMPORT SUMMARY")
    print("=" * 60)
    print(f"✅ Imported: {len(imported)}")
    for name, wf_id in imported:
        print(f"   - {name} (ID: {wf_id})")
    
    if skipped:
        print(f"\n⏭️  Skipped (already exist): {len(skipped)}")
        for name, wf_name in skipped:
            print(f"   - {name} ({wf_name})")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for name, error in failed:
            print(f"   - {name}: {error}")
    
    print("\n" + "=" * 60)
    print("✅ N8N Automation Setup Complete")
    print("\n💡 Next Steps:")
    print("   1. Review workflows in N8N UI: http://localhost:5678")
    print("   2. Configure PostgreSQL credentials in workflows")
    print("   3. Configure SSH credentials (for executeCommand nodes)")
    print("   4. Test workflows manually before full automation")
    print("   5. Monitor executions in N8N dashboard")
    print("=" * 60)

if __name__ == '__main__':
    main()

