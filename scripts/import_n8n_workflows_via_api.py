#!/usr/bin/env python3
"""
Import n8n Workflows via API
Uses Basic Auth (web UI credentials) to import workflows

Author: Claude for Arthur
Date: October 30, 2025
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

# Workflow files
WORKFLOW_DIR = Path("/Users/arthurdell/AYA/n8n_workflows")
WORKFLOWS = [
    "code-validator-main.json",
    "code-validator-file-watcher.json",
    "code-validator-scheduled-audit.json"
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


def import_workflow(session, workflow_file):
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
    
    # Try to import via workflow import endpoint (might be different)
    # First, try the standard create endpoint
    try:
        response = session.post(
            f'{N8N_URL}/api/v1/workflows',
            json=workflow_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "workflow_id": result.get('id'),
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


def main():
    print("=" * 60)
    print("N8N Workflow Import via API")
    print("=" * 60)
    print()
    
    # Create authenticated session
    print(f"🔐 Authenticating to {N8N_URL}...")
    session = get_auth_session()
    
    # Test connection
    try:
        response = session.get(f'{N8N_URL}/healthz', timeout=5)
        if response.status_code == 200:
            print("✅ Connected to n8n\n")
        else:
            print(f"⚠️  Health check returned: {response.status_code}\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        return 1
    
    # Import workflows
    results = []
    for workflow_file in WORKFLOWS:
        print(f"📦 Importing: {workflow_file}...")
        result = import_workflow(session, workflow_file)
        results.append(result)
        
        if result.get("success"):
            workflow_id = result.get("workflow_id")
            print(f"   ✅ Success! ID: {workflow_id}")
            print(f"   👀 View: {N8N_URL}/workflow/{workflow_id}\n")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}\n")
    
    # Summary
    print("=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r.get("success"))
    print(f"✅ Successfully imported: {successful}/{len(WORKFLOWS)}")
    print()
    
    for result in results:
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {result.get('name', result.get('file', 'Unknown'))}")
        if result.get("success"):
            print(f"   ID: {result.get('workflow_id')}")
            print(f"   URL: {N8N_URL}/workflow/{result.get('workflow_id')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')[:80]}")
        print()
    
    if successful == len(WORKFLOWS):
        print("🎉 All workflows imported successfully!")
        print("\nNext steps:")
        print("1. Open n8n UI: http://localhost:5678")
        print("2. Activate workflows (toggle switch)")
        print("3. Configure PostgreSQL credentials in each workflow")
        return 0
    else:
        print("⚠️  Some workflows failed to import")
        print("   You may need to import them manually via n8n UI")
        return 1


if __name__ == '__main__':
    sys.exit(main())

