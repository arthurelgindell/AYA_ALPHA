#!/usr/bin/env python3
"""
Import Intelligence Scout Workflows via N8N API
Uses N8N API directly (simulating MCP server calls)
"""

import json
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load N8N configuration
env_file = Path(__file__).parent.parent.parent / 'mcp_servers' / 'n8n-mcp' / '.env'
if env_file.exists():
    load_dotenv(env_file)

N8N_API_URL = os.getenv('N8N_API_URL', 'http://localhost:5678')
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

if not N8N_API_KEY:
    print("❌ N8N_API_KEY not found")
    sys.exit(1)

HEADERS = {
    'X-N8N-API-KEY': N8N_API_KEY,
    'Content-Type': 'application/json'
}

def n8n_health_check():
    """Check N8N health (simulating MCP tool)"""
    try:
        response = requests.get(f"{N8N_API_URL}/api/v1/health", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        return {'success': False, 'error': f"Status {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def n8n_list_workflows(active_only=None):
    """List workflows (simulating MCP tool)"""
    try:
        params = {}
        if active_only is not None:
            params['active'] = str(active_only).lower()
        
        response = requests.get(f"{N8N_API_URL}/api/v1/workflows", headers=HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            return {'success': True, 'data': response.json().get('data', [])}
        return {'success': False, 'error': f"Status {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def n8n_create_workflow(workflow_data):
    """Create workflow (simulating MCP tool)"""
    try:
        # Remove ID if present
        if 'id' in workflow_data:
            del workflow_data['id']
        
        # Ensure inactive initially for safety
        workflow_data['active'] = False
        
        response = requests.post(
            f"{N8N_API_URL}/api/v1/workflows",
            headers=HEADERS,
            json=workflow_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('id') or result.get('data', {}).get('id')
            return {'success': True, 'workflow_id': workflow_id, 'data': result}
        return {'success': False, 'error': f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def n8n_activate_workflow(workflow_id):
    """Activate workflow"""
    try:
        response = requests.post(
            f"{N8N_API_URL}/api/v1/workflows/{workflow_id}/activate",
            headers=HEADERS,
            timeout=10
        )
        return {'success': response.status_code == 200, 'status_code': response.status_code}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    """Main execution"""
    print("🚀 Intelligence Scout - N8N Workflow Import")
    print("=" * 60)
    
    # 1. Health check
    print("\n1️⃣ Checking N8N health...")
    health = n8n_health_check()
    if not health['success']:
        print(f"❌ N8N health check failed: {health.get('error', 'Unknown error')}")
        print(f"   URL: {N8N_API_URL}")
        sys.exit(1)
    print("✅ N8N is healthy")
    
    # 2. List existing workflows
    print("\n2️⃣ Checking existing workflows...")
    workflows_result = n8n_list_workflows()
    if workflows_result['success']:
        existing_workflows = workflows_result['data']
        existing_names = {w.get('name') for w in existing_workflows}
        print(f"   Found {len(existing_workflows)} existing workflows")
    else:
        print(f"⚠️  Could not list workflows: {workflows_result.get('error')}")
        existing_workflows = []
        existing_names = set()
    
    # 3. Load and import workflows
    workflows_dir = Path(__file__).parent / 'n8n_workflows'
    
    workflows_to_import = [
        ('crawl_scheduler_failsafe.json', 'Intelligence Scout - Failsafe Crawl Scheduler'),
        ('result_monitor.json', 'Intelligence Scout - Result Monitor'),
    ]
    
    imported = []
    updated = []
    failed = []
    
    print("\n3️⃣ Importing workflows...")
    for filename, expected_name in workflows_to_import:
        filepath = workflows_dir / filename
        
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            failed.append((filename, "File not found"))
            continue
        
        # Check if exists
        existing_workflow = None
        for wf in existing_workflows:
            if wf.get('name') == expected_name:
                existing_workflow = wf
                break
        
        # Load workflow
        print(f"📥 Processing {filename}...")
        try:
            with open(filepath) as f:
                workflow_data = json.load(f)
            
            # Update name to match expected
            workflow_data['name'] = expected_name
            
            if existing_workflow:
                print(f"   ⚠️  Workflow '{expected_name}' already exists (ID: {existing_workflow.get('id')})")
                print(f"   💡 Skipping import - workflow may need manual update")
                updated.append((filename, existing_workflow.get('id'), existing_workflow.get('active', False)))
            else:
                # Create new workflow
                result = n8n_create_workflow(workflow_data)
                
                if result['success']:
                    workflow_id = result['workflow_id']
                    print(f"   ✅ Created workflow (ID: {workflow_id})")
                    
                    # Activate workflow
                    activate_result = n8n_activate_workflow(workflow_id)
                    if activate_result['success']:
                        print(f"   ✅ Activated workflow")
                        imported.append((filename, workflow_id, True))
                    else:
                        print(f"   ⚠️  Created but not activated: {activate_result.get('error', 'Unknown')}")
                        imported.append((filename, workflow_id, False))
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
    
    if imported:
        print(f"\n✅ Imported: {len(imported)}")
        for name, wf_id, active in imported:
            status = "ACTIVE" if active else "INACTIVE"
            print(f"   - {name}")
            print(f"     ID: {wf_id}, Status: {status}")
    
    if updated:
        print(f"\n⏭️  Already Exists: {len(updated)}")
        for name, wf_id, active in updated:
            status = "ACTIVE" if active else "INACTIVE"
            print(f"   - {name} (ID: {wf_id}, Status: {status})")
            print(f"     → Consider updating manually in N8N UI if needed")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for name, error in failed:
            print(f"   - {name}: {error}")
    
    print("\n" + "=" * 60)
    print("✅ N8N Workflow Import Complete")
    print("\n💡 Next Steps:")
    print("   1. Review workflows in N8N UI: http://localhost:5678")
    print("   2. Configure credentials (PostgreSQL, SSH)")
    print("   3. Test workflows manually")
    print("   4. Verify automation is working")
    print("=" * 60)

if __name__ == '__main__':
    main()

