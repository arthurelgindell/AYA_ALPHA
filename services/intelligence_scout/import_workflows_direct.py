#!/usr/bin/env python3
"""
Direct N8N Workflow Import - Retry with better error handling
"""

import json
import os
import sys
import requests
import time
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

def wait_for_n8n(max_wait=30):
    """Wait for N8N to be ready"""
    print("⏳ Waiting for N8N to be ready...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{N8N_API_URL}/api/v1/workflows", headers=HEADERS, timeout=3)
            if response.status_code in [200, 401]:  # 401 means service is up but auth issue
                print("✅ N8N is responding")
                return True
        except:
            pass
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   Still waiting... ({i+1}/{max_wait}s)")
    return False

def create_workflow(workflow_data):
    """Create workflow with retry"""
    workflow_data = workflow_data.copy()
    if 'id' in workflow_data:
        del workflow_data['id']
    workflow_data['active'] = False  # Start inactive for safety
    
    for attempt in range(3):
        try:
            response = requests.post(
                f"{N8N_API_URL}/api/v1/workflows",
                headers=HEADERS,
                json=workflow_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'workflow_id': result.get('id') or result.get('data', {}).get('id'),
                    'data': result
                }
            elif response.status_code == 503:
                if attempt < 2:
                    print(f"   ⚠️  Service temporarily unavailable, retrying... ({attempt+1}/3)")
                    time.sleep(5)
                    continue
                return {'success': False, 'error': f"Service unavailable (503)"}
            else:
                return {'success': False, 'error': f"Status {response.status_code}: {response.text[:200]}"}
        except requests.exceptions.RequestException as e:
            if attempt < 2:
                time.sleep(3)
                continue
            return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'Max retries exceeded'}

def main():
    print("🚀 Intelligence Scout - N8N Workflow Import (Direct)")
    print("=" * 60)
    
    if not wait_for_n8n():
        print("❌ N8N is not responding. Please ensure N8N service is running.")
        print(f"   URL: {N8N_API_URL}")
        print("\n💡 Check N8N status:")
        print("   docker ps | grep n8n")
        print("   docker logs n8n-main")
        sys.exit(1)
    
    # Load workflows
    workflows_dir = Path(__file__).parent / 'n8n_workflows'
    workflows_to_import = [
        ('crawl_scheduler_failsafe.json', 'Intelligence Scout - Failsafe Crawl Scheduler'),
        ('result_monitor.json', 'Intelligence Scout - Result Monitor'),
    ]
    
    imported = []
    failed = []
    
    print("\n📥 Importing workflows...\n")
    
    for filename, expected_name in workflows_to_import:
        filepath = workflows_dir / filename
        
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            failed.append((filename, "File not found"))
            continue
        
        print(f"Importing: {filename}")
        try:
            with open(filepath) as f:
                workflow_data = json.load(f)
            
            workflow_data['name'] = expected_name
            
            result = create_workflow(workflow_data)
            
            if result['success']:
                workflow_id = result['workflow_id']
                print(f"   ✅ Created workflow ID: {workflow_id}")
                
                # Try to activate
                try:
                    activate_response = requests.post(
                        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}/activate",
                        headers=HEADERS,
                        timeout=10
                    )
                    if activate_response.status_code == 200:
                        print(f"   ✅ Activated")
                        imported.append((filename, workflow_id, True))
                    else:
                        print(f"   ⚠️  Created but not activated (you can activate manually in UI)")
                        imported.append((filename, workflow_id, False))
                except Exception as e:
                    print(f"   ⚠️  Created but activation failed: {e}")
                    imported.append((filename, workflow_id, False))
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
                failed.append((filename, result.get('error', 'Unknown')))
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed.append((filename, str(e)))
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Imported: {len(imported)}")
    for name, wf_id, active in imported:
        print(f"   - {name} (ID: {wf_id}) {'[ACTIVE]' if active else '[INACTIVE - activate in UI]'}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for name, error in failed:
            print(f"   - {name}: {error}")
    
    if imported:
        print("\n💡 Next Steps:")
        print(f"   1. Review workflows: {N8N_API_URL}")
        print("   2. Configure credentials (PostgreSQL, SSH)")
        print("   3. Test workflows manually")
        print("   4. Activate if not already active")
    
    print("=" * 60)

if __name__ == '__main__':
    main()

