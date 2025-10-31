# n8n Access Information

**For**: Arthur  
**Status**: ✅ n8n is Running  
**Date**: October 30, 2025

---

## Local Access (On ALPHA)

**URL**: http://localhost:5678

**Credentials**:
- **Username**: `arthur`
- **Password**: `BebyJK00n3w+uwHMlKA67Q==`

**Status**: ✅ n8n-main container is running and accessible

---

## Remote Access (Via Tailscale)

**URL**: http://alpha.tail5f2bae.ts.net:5678

**Credentials**: Same as above

**Note**: Requires Tailscale connection

---

## Quick Access

### From Terminal

```bash
# Open in default browser
open http://localhost:5678

# Or copy this URL:
echo "http://localhost:5678"
```

### From Browser

Simply navigate to: **http://localhost:5678**

---

## Import Code Validation Workflows

Once you're in n8n:

1. Click **"Workflows"** in the left sidebar
2. Click **"Import from File"** (top right)
3. Select files from `/Users/arthurdell/AYA/n8n_workflows/`:
   - `code-validator-main.json`
   - `code-validator-file-watcher.json`
   - `code-validator-scheduled-audit.json`

**Detailed Instructions**: See `n8n_workflows/QUICK_IMPORT_GUIDE.md`

---

## Docker Status

**Container**: `n8n-main`  
**Port**: `5678`  
**Status**: ✅ Running  
**Workers**: 3 workers running  

**View Status**:
```bash
docker ps | grep n8n
```

---

## Troubleshooting

### Can't Access http://localhost:5678

1. **Check if container is running**:
   ```bash
   docker ps | grep n8n-main
   ```

2. **Check port binding**:
   ```bash
   lsof -i :5678
   ```

3. **Restart n8n** (if needed):
   ```bash
   cd ~/N8N/docker
   docker-compose restart n8n-main
   ```

4. **View logs**:
   ```bash
   docker logs n8n-main --tail 50
   ```

---

## Summary

✅ **n8n is running and accessible**  
✅ **Local URL**: http://localhost:5678  
✅ **Credentials**: arthur / BebyJK00n3w+uwHMlKA67Q==  
✅ **Ready for workflow import**  

**Open**: http://localhost:5678 in your browser!

