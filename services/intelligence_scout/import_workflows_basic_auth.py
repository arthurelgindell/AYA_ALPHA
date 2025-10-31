#!/usr/bin/env python3
"""
Import Intelligence Scout Workflows via N8N API
Uses Basic Auth (web UI credentials) - same method as existing workflow imports
"""

import sys
import json
import requests
import base64
from pathlib import Path

# Configuration
N8N_URL = "http://localhost:5678"
USERNAME = "arthur"
PASSWORD = "BebyJK00n3w+uwHMlKA67Q=="  # From docker-compose.yml

# Load API key from environment
import os
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent.parent / 'mcp_servers' / 'n8n-mcp' / '.env'
if env_file.exists():
    load_dotenv(env_file)
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

# Workflow files
WORKFLOW_DIR = Path(__file__).parent / 'n8n_workflows'
WORKFLOWS = [
    "crawl_scheduler_failsafe.json",
    "result_monitor.json"
]


def get_auth_session():
    """Create authenticated session using Basic Auth (web UI)"""
    session = requests.Session()
    
    # Basic Auth for web UI
    auth_header = base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
    session.headers.update({
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/json'
    })
    
    return session


def list_existing_workflows(session):
    """List existing workflows to check for duplicates"""
    try:
        response = session.get(f'{N8N_URL}/api/v1/workflows', timeout=10)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        print(f"⚠️  Could not list workflows: {e}")
        return []


def import_workflow(session, workflow_file, api_key):
    """Import a single workflow"""
    file_path = WORKFLOW_DIR / workflow_file
    
    if not file_path.exists():
        return {
            "success": False,
            "error": f"File not found: {workflow_file}"
        }
    
    # Read workflow JSON
    with open(file_path, 'r') as f:
        workflow_data = json.load(f)
    
    workflow_name = workflow_data.get('name', workflow_file.replace('.json', ''))
    
    # Clean workflow for API import - remove read-only fields
    # Remove read-only fields that cause API errors
    for field in ['id', 'active', 'createdAt', 'updatedAt', 'triggerCount', 'versionId', 'pinData', 'staticData', 'tags']:
        workflow_data.pop(field, None)
    
    # Clean settings - remove problematic fields
    if 'settings' in workflow_data:
        # Keep only essential settings
        if 'saveManualExecutions' in workflow_data.get('settings', {}):
            del workflow_data['settings']['saveManualExecutions']
        if 'saveExecutionProgress' in workflow_data.get('settings', {}):
            del workflow_data['settings']['saveExecutionProgress']
        if workflow_data.get('settings') == {}:
            del workflow_data['settings']
    
    # Clean nodes - remove node IDs (n8n will reassign)
    if 'nodes' in workflow_data:
        for node in workflow_data['nodes']:
            if 'id' in node:
                del node['id']
    
    # Create headers with both Basic Auth and API Key
    headers = session.headers.copy()
    if api_key:
        headers['X-N8N-API-KEY'] = api_key
    
    try:
        response = session.post(
            f'{N8N_URL}/api/v1/workflows',
            json=workflow_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('id') or result.get('data', {}).get('id')
            return {
                "success": True,
                "workflow_id": workflow_id,
                "name": workflow_name,
                "file": workflow_file
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "name": workflow_name
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "name": workflow_name
        }


def activate_workflow(session, workflow_id, api_key):
    """Activate a workflow"""
    headers = session.headers.copy()
    if api_key:
        headers['X-N8N-API-KEY'] = api_key
    
    try:
        response = session.post(
            f'{N8N_URL}/api/v1/workflows/{workflow_id}/activate',
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"   ⚠️  Activation failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Intelligence Scout - N8N Workflow Import")
    print("=" * 60)
    print()
    
    # Create authenticated session
    print(f"🔐 Authenticating to {N8N_URL}...")
    session = get_auth_session()
    
    # Test connection using healthz endpoint
    try:
        response = session.get(f'{N8N_URL}/healthz', timeout=5)
        if response.status_code == 200:
            print("✅ Connected to n8n\n")
        else:
            print(f"⚠️  Health check returned: {response.status_code}")
            print("   Attempting to continue anyway...\n")
    except Exception as e:
        print(f"⚠️  Health check failed: {e}")
        print("   Attempting to continue anyway...\n")
    
    # List existing workflows
    print("🔍 Checking existing workflows...")
    existing_workflows = list_existing_workflows(session)
    existing_names = {w.get('name') for w in existing_workflows}
    print(f"   Found {len(existing_workflows)} existing workflows\n")
    
    # Import workflows
    results = []
    for workflow_file in WORKFLOWS:
        workflow_path = WORKFLOW_DIR / workflow_file
        if not workflow_path.exists():
            print(f"⚠️  Skipping {workflow_file} (file not found)")
            continue
        
        with open(workflow_path) as f:
            workflow_data = json.load(f)
        
        workflow_name = workflow_data.get('name', workflow_file.replace('.json', ''))
        
        # Check if already exists
        if workflow_name in existing_names:
            print(f"⏭️  Skipping {workflow_file}")
            print(f"   Workflow '{workflow_name}' already exists\n")
            # Find existing workflow ID
            existing_wf = next((w for w in existing_workflows if w.get('name') == workflow_name), None)
            if existing_wf:
                results.append({
                    "success": True,
                    "workflow_id": existing_wf.get('id'),
                    "name": workflow_name,
                    "file": workflow_file,
                    "existing": True
                })
            continue
        
        print(f"📦 Importing: {workflow_file}...")
        result = import_workflow(session, workflow_file, N8N_API_KEY)
        results.append(result)
        
        if result.get("success"):
            workflow_id = result.get("workflow_id")
            print(f"   ✅ Success! ID: {workflow_id}")
            
            # Try to activate
            if activate_workflow(session, workflow_id, N8N_API_KEY):
                print(f"   ✅ Activated workflow")
                result["activated"] = True
            else:
                print(f"   ⚠️  Created but not activated (activate manually in UI)")
                result["activated"] = False
            
            print(f"   👀 View: {N8N_URL}/workflow/{workflow_id}\n")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}\n")
    
    # Summary
    print("=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r.get("success"))
    existing_count = sum(1 for r in results if r.get("existing"))
    print(f"✅ Successfully imported: {successful}/{len([w for w in WORKFLOWS if (WORKFLOW_DIR / w).exists()])}")
    if existing_count > 0:
        print(f"⏭️  Already exists: {existing_count}")
    print()
    
    for result in results:
        if result.get("existing"):
            status = "⏭️ "
        elif result.get("success"):
            status = "✅"
        else:
            status = "❌"
            
        print(f"{status} {result.get('name', result.get('file', 'Unknown'))}")
        if result.get("success"):
            print(f"   ID: {result.get('workflow_id')}")
            print(f"   URL: {N8N_URL}/workflow/{result.get('workflow_id')}")
            if result.get("existing"):
                print(f"   Status: Already exists")
            elif result.get("activated"):
                print(f"   Status: Active")
            else:
                print(f"   Status: Created but not activated")
        else:
            print(f"   Error: {result.get('error', 'Unknown')[:80]}")
        print()
    
    if successful == len([w for w in WORKFLOWS if (WORKFLOW_DIR / w).exists()]):
        print("🎉 All workflows imported successfully!")
        print("\n💡 Next steps:")
        print("1. Open n8n UI: http://localhost:5678")
        print("2. Review workflows and configure credentials:")
        print("   - PostgreSQL credentials for database queries")
        print("   - SSH credentials (optional, for executeCommand nodes)")
        print("3. Activate workflows if not already active")
        print("4. Test workflows manually before relying on automation")
        return 0
    else:
        print("⚠️  Some workflows failed to import")
        print("   You may need to import them manually via n8n UI")
        return 1


if __name__ == '__main__':
    sys.exit(main())

