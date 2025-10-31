# n8n API Key Setup Required

**Issue**: The API key you provided isn't registered in n8n's database.

**Status**: ❌ API key authentication failing  
**Solution**: Create API key through n8n UI

---

## Problem

The JWT token you provided:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTE4YjNlMy1hNjhmLTRkMzctYjJjZC1iNTI2ZTcyYjY5NWQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNjU3MTU4fQ.cq0q6bZUwy1wnxqm5TKqycST3p5jBmyp_3eHayC8sHo
```

- ✅ Valid JWT format
- ✅ Token age: 1.4 days (not expired)
- ❌ **Not registered in n8n's `user_api_keys` table**

n8n requires API keys to be created through its web interface, which stores them in the database. The token you provided isn't in the database, so n8n rejects it.

---

## Solution: Create API Key in n8n UI

### Step 1: Open n8n UI

```
URL: http://localhost:5678
Username: arthur
Password: BebyJK00n3w+uwHMlKA67Q==
```

### Step 2: Create API Key

1. Log in to n8n
2. Click **Settings** (gear icon, top right)
3. Go to **API Keys** section
4. Click **Create API Key**
5. Name it: `Cursor MCP Server` or `Code Validator Import`
6. **Copy the API key** (you'll only see it once!)

### Step 3: Update Configuration

Once you have the new API key, I can:

1. Update `/Users/arthurdell/AYA/mcp_servers/n8n-mcp/.env`
2. Use the n8n MCP server to import all 3 workflows automatically

---

## Alternative: Manual Import (Fastest Right Now)

Since API key setup requires manual steps, **you can import workflows manually** in ~2 minutes:

1. **Open n8n**: http://localhost:5678
2. **Login** with credentials above
3. **Click "Workflows"** → **"Import from File"**
4. **Import these 3 files**:
   - `/Users/arthurdell/AYA/n8n_workflows/code-validator-main.json`
   - `/Users/arthurdell/AYA/n8n_workflows/code-validator-file-watcher.json`
   - `/Users/arthurdell/AYA/n8n_workflows/code-validator-scheduled-audit.json`

---

## Next Steps

**Option A** (Recommended for automation):
1. Create API key in n8n UI
2. Share the new API key with me
3. I'll update config and import via MCP server

**Option B** (Quickest right now):
1. Import workflows manually via UI (~2 minutes)
2. Set up API key later for future automation

---

**Which would you prefer?**

