# Importing n8n Workflows via MCP Server

**Status**: ✅ MCP Server Ready, ⚠️ API Key Required  
**Date**: October 30, 2025

---

## The Situation

You asked if we can import workflows using the **n8n MCP server** we built. The answer is **YES, but** we need a valid n8n API key first.

**Current Issue**: 
- ✅ n8n MCP server is built and configured
- ✅ n8n client library can create workflows
- ❌ API key authentication is failing (401 Unauthorized)

---

## Solution: Create API Key Through n8n UI

n8n requires API keys to be created through its web interface (Settings > API Keys). Once you have a valid API key, we can use the MCP server to import workflows programmatically.

### Step 1: Create API Key in n8n UI

1. **Open n8n**: http://localhost:5678
2. **Login** with credentials:
   - Username: `arthur`
   - Password: `BebyJK00n3w+uwHMlKA67Q==`
3. **Go to Settings** > **API Keys** (or `/settings/api-keys`)
4. **Create New API Key**:
   - Name: `Cursor MCP Server`
   - Click **Create**
   - **Copy the API key** (you'll only see it once!)

### Step 2: Update MCP Server Configuration

Once you have the API key, update the `.env` file:

```bash
# Edit the .env file
nano /Users/arthurdell/AYA/mcp_servers/n8n-mcp/.env

# Update this line with your actual API key:
N8N_API_KEY=<paste_your_api_key_here>
```

### Step 3: Import Workflows via MCP Server

Once the API key is configured, you can ask me (Claude) to:

1. **Use the MCP server** to import workflows:
   ```
   "Use the n8n MCP server to import the code validation workflows"
   ```

2. **Or run directly**:
   ```bash
   cd /Users/arthurdell/AYA
   python3 << 'EOF'
   import sys
   sys.path.insert(0, '/Users/arthurdell/AYA/mcp_servers/n8n-mcp')
   from n8n_client import N8NClient
   import json
   from pathlib import Path
   import os
   from dotenv import load_dotenv
   
   load_dotenv('/Users/arthurdell/AYA/mcp_servers/n8n-mcp/.env')
   
   client = N8NClient(
       os.getenv('N8N_API_URL', 'http://localhost:5678'),
       os.getenv('N8N_API_KEY')
   )
   
   # Import workflows...
   EOF
   ```

---

## Alternative: Manual Import (Current Workaround)

Since API key setup requires manual steps, the **quickest way right now** is:

1. **Open n8n UI**: http://localhost:5678
2. **Click "Workflows"** → **"Import from File"**
3. **Import these 3 files**:
   - `/Users/arthurdell/AYA/n8n_workflows/code-validator-main.json`
   - `/Users/arthurdell/AYA/n8n_workflows/code-validator-file-watcher.json`
   - `/Users/arthurdell/AYA/n8n_workflows/code-validator-scheduled-audit.json`

**Time**: ~2 minutes (faster than API key setup for first-time)

---

## Why Can't We Use Basic Auth?

n8n's REST API (`/api/v1/*`) **requires API key authentication** (`X-N8N-API-KEY` header). Basic Auth is only for the web UI, not the API.

The MCP server is designed to use the API, so it needs an API key.

---

## Once API Key is Configured

After you create the API key and update the `.env` file, you can say:

> "Use the n8n MCP server to import all three code validation workflows"

And I'll use the `n8n_create_workflow` MCP tool to import them programmatically.

---

## Summary

**Can we use the MCP server?**: ✅ **YES**  
**Is it ready?**: ✅ **YES**  
**What's missing?**: ⚠️ **API Key** (needs to be created in n8n UI)  

**Quickest path right now**: Manual import via UI (2 minutes)  
**Long-term solution**: Create API key → Use MCP server for future imports

