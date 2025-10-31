# n8n Admin URLs

**For**: Arthur  
**Date**: October 30, 2025

---

## Main URLs

### n8n Home Page
```
http://localhost:5678
```

### Direct Login (if needed)
```
http://localhost:5678/login
```

**Credentials**:
- **Username**: `arthur`
- **Password**: `BebyJK00n3w+uwHMlKA67Q==`

---

## API Key Management

### Settings Page (API Keys)
```
http://localhost:5678/settings/api-keys
```

**Direct path**: Settings → API Keys (after login)

---

## Quick Steps to Create API Key

1. **Open**: http://localhost:5678
2. **Login** with credentials above
3. **Go to**: http://localhost:5678/settings/api-keys
   - Or click **Settings** (gear icon) → **API Keys**
4. **Click**: "Create API Key" button
5. **Name it**: `Cursor MCP Server` or `Code Validator Import`
6. **Copy the key** (only shown once!)

---

## After Creating API Key

Once you have the new API key, share it with me and I'll:
1. Update `/Users/arthurdell/AYA/mcp_servers/n8n-mcp/.env`
2. Import all 3 code validation workflows via the MCP server
3. Verify everything is working

---

## Workflow Management

### View All Workflows
```
http://localhost:5678/workflows
```

### Import Workflows Manually (if needed)
```
http://localhost:5678/workflows
```
Then click "Import from File" (top right)

---

## Summary

✅ **Main URL**: http://localhost:5678  
✅ **API Keys Page**: http://localhost:5678/settings/api-keys  
✅ **Workflows Page**: http://localhost:5678/workflows  

**Ready to create API key!**

