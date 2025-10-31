# Fixing n8n Workflow Activation Errors

**Issue**: "propertyValues[itemName] is not iterable" error when activating workflows  
**Cause**: PostgreSQL credential references in workflow nodes  
**Date**: October 30, 2025

---

## Problem

Two workflows fail to activate:
- Code Validator - Main Validation Workflow
- Code Validator - File Watcher

Error: `propertyValues[itemName] is not iterable`

This happens because the PostgreSQL nodes reference credentials that don't exist or aren't properly configured in n8n.

---

## Solution: Manual Fix in n8n UI

### Step 1: Open Each Workflow

1. **Code Validator - Main Validation Workflow**
   - URL: http://localhost:5678/workflow/hM7Luk6hFyAExH7y

2. **Code Validator - File Watcher**
   - URL: http://localhost:5678/workflow/2CJUnViEIfFtoCZl

### Step 2: Fix PostgreSQL Nodes

For each workflow:

1. **Click on the PostgreSQL node** (e.g., "Log to PostgreSQL" or "Log Validation")
2. **In the node configuration**:
   - If you see credential errors, click **"Reset"** or **"Remove Credentials"**
   - Or click **"Edit Credentials"** → **"Create New"**
3. **Configure PostgreSQL credentials**:
   - **Host**: `host.docker.internal`
   - **Port**: `5432`
   - **Database**: `aya_rag`
   - **User**: `postgres`
   - **Password**: `Power$$336633$$`
   - **SSL**: Disabled (or enabled if needed)
4. **Click "Save"** to save credentials
5. **Click "Save"** on the workflow

### Step 3: Activate Workflow

1. After fixing credentials, toggle the **"Active"** switch
2. Workflow should activate successfully

---

## Alternative: Re-import Workflows Without Credentials

If manual fix doesn't work, you can:

1. **Delete the failing workflows** in n8n UI
2. **Re-import** without credential references:

The workflow files in `/Users/arthurdell/AYA/n8n_workflows/` have credential references. You can:

**Option A**: Import manually and configure credentials in UI
**Option B**: Remove credential references from JSON files and re-import

---

## Why Scheduled Daily Audit Works

The "Code Validator - Scheduled Daily Audit" workflow works because:
- It may have credentials already configured
- Or its PostgreSQL nodes don't have the problematic credential reference

---

## Quick Fix Script

Run this to check current status:

```bash
cd /Users/arthurdell/AYA
python3 << 'EOF'
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('/Users/arthurdell/AYA/mcp_servers/n8n-mcp/.env'))
sys.path.insert(0, '/Users/arthurdell/AYA/mcp_servers/n8n-mcp')
from n8n_client import N8NClient

api_url = os.getenv('N8N_API_URL', 'http://localhost:5678')
api_key = os.getenv('N8N_API_KEY')
client = N8NClient(api_url, api_key)

workflows = client.list_workflows()
for wf in workflows:
    if 'Code Validator' in wf.get('name', ''):
        print(f"{'✅' if wf.get('active') else '❌'} {wf.get('name')} - {wf.get('id')}")
EOF
```

---

## Summary

**Root Cause**: PostgreSQL credential references in workflow nodes  
**Fix**: Configure credentials manually in n8n UI  
**Time**: ~2 minutes per workflow

After fixing credentials, workflows should activate successfully.

