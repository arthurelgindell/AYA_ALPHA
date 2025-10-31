# Quick n8n Workflow Import Guide

**For**: Arthur  
**Time Required**: 5-10 minutes  
**Status**: Ready to Import

---

## Quick Import Steps

### 1. Access n8n UI

```
URL: http://localhost:5678
(or http://alpha.tail5f2bae.ts.net:5678)
Username: arthur
Password: (check your n8n credentials)
```

### 2. Import Workflows (3 workflows)

For each workflow file in `/Users/arthurdell/AYA/n8n_workflows/`:

1. Click **"Workflows"** in left sidebar
2. Click **"Import from File"** (top right)
3. Select the JSON file:
   - `code-validator-main.json` (Main validation webhook)
   - `code-validator-file-watcher.json` (File monitoring)
   - `code-validator-scheduled-audit.json` (Daily reports)
4. Click **"Import"**

### 3. Configure PostgreSQL Credentials

After importing each workflow:

1. Find the **PostgreSQL** node(s)
2. Click on the node
3. Click **"Edit Credentials"**
4. Configure:
   - **Host**: `host.docker.internal` (if n8n in Docker) or `localhost`
   - **Port**: `5432`
   - **Database**: `aya_rag`
   - **User**: `postgres`
   - **Password**: `Power$$336633$$`
5. Click **"Save"**

### 4. Configure SMTP (Optional - for daily audit only)

Only needed for `code-validator-scheduled-audit.json`:

1. Find the **Email Send** node
2. Click **"Edit Credentials"**
3. Configure your SMTP settings
4. Update email recipient from `arthur@aya.local` to your email
5. Click **"Save"**

### 5. Activate Workflows

For each workflow:

1. Click the **"Active"** toggle (top right)
2. Workflow is now active!

---

## Workflow Details

### Workflow 1: Code Validator - Main

**Purpose**: Webhook endpoint for code validation  
**Webhook URL**: `http://localhost:5678/webhook/code-validate`  
**Triggers**: HTTP POST requests  
**Status**: ✅ Ready to import

**Test**:
```bash
curl -X POST http://localhost:5678/webhook/code-validate \
  -H "Content-Type: application/json" \
  -d '{"code": "def test(): pass", "agent_name": "test"}'
```

### Workflow 2: Code Validator - File Watcher

**Purpose**: Automatically validate files when they change  
**Triggers**: Every 5 minutes  
**Status**: ✅ Ready to import

**Note**: Requires `find` command. Adjust file paths if needed.

### Workflow 3: Code Validator - Scheduled Daily Audit

**Purpose**: Generate daily compliance reports  
**Triggers**: Daily at 2 AM  
**Status**: ✅ Ready to import (SMTP optional)

**Note**: Update email recipient and configure SMTP if needed.

---

## Verification Checklist

After importing:

- [ ] All 3 workflows imported successfully
- [ ] PostgreSQL credentials configured
- [ ] Main workflow activated
- [ ] File watcher activated (optional)
- [ ] Daily audit activated (optional)
- [ ] Webhook endpoint tested
- [ ] Database logging verified

---

## Troubleshooting

### Import Failed

**Error**: "Invalid workflow format"
- **Fix**: Ensure you're importing JSON files, not YAML
- **Fix**: Check file paths are correct

### PostgreSQL Connection Failed

**Error**: "Connection refused"
- **Fix**: Use `host.docker.internal` if n8n is in Docker
- **Fix**: Verify PostgreSQL is running: `psql -h localhost -U postgres -d aya_rag`

### Webhook Not Responding

**Error**: "404 Not Found"
- **Fix**: Ensure workflow is activated
- **Fix**: Check webhook path matches workflow configuration

---

## Quick Test After Import

```bash
# Test webhook endpoint
curl -X POST http://localhost:5678/webhook/code-validate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(): print(\"Hello\")",
    "agent_name": "import_test"
  }'

# Check database
PGPASSWORD='Power$$336633$$' psql -h localhost -U postgres -d aya_rag \
  -c "SELECT validation_id, agent_name, enforcement_action FROM code_validations ORDER BY validation_time DESC LIMIT 1;"
```

---

## Summary

✅ **3 Workflows Ready**  
✅ **Import Instructions Provided**  
✅ **Configuration Documented**  
✅ **Test Commands Ready**  

**Estimated Import Time**: 5-10 minutes  
**Status**: Ready for import!

