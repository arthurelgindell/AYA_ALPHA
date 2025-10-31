# n8n Workflows for Code Validation

**Location**: `/Users/arthurdell/AYA/n8n_workflows/`  
**Status**: Ready for Import  
**Instructions**: Import these workflows into n8n UI

---

## Workflows Included

### 1. Code Validator - Main Validation Workflow

**File**: `code-validator-main.json`

**Purpose**: Main webhook endpoint for code validation requests

**Features**:
- Receives validation requests via webhook
- Executes code validator script
- Logs results to PostgreSQL
- Returns enforcement decision (block/warn/pass)

**Webhook URL**: `http://localhost:5678/webhook/code-validate`

**Import Steps**:
1. Open n8n UI: http://localhost:5678
2. Click "Workflows" → "Import from File"
3. Select `code-validator-main.json`
4. Configure PostgreSQL credentials
5. Activate workflow

---

### 2. Code Validator - File Watcher

**File**: `code-validator-file-watcher.json`

**Purpose**: Automatically validate files when they change

**Features**:
- Runs every 5 minutes
- Finds recently modified code files
- Validates up to 8 files in parallel (80B MLX capacity)
- Logs all validations to database

**Import Steps**:
1. Open n8n UI
2. Click "Workflows" → "Import from File"
3. Select `code-validator-file-watcher.json`
4. Configure PostgreSQL credentials
5. Activate workflow

**Note**: This workflow requires the `find` command and may need adjustments for your system.

---

### 3. Code Validator - Scheduled Daily Audit

**File**: `code-validator-scheduled-audit.json`

**Purpose**: Generate daily compliance reports

**Features**:
- Runs daily at 2 AM
- Aggregates validation metrics
- Updates compliance_metrics table
- Sends email report (requires SMTP configuration)

**Import Steps**:
1. Open n8n UI
2. Click "Workflows" → "Import from File"
3. Select `code-validator-scheduled-audit.json`
4. Configure PostgreSQL credentials
5. Configure SMTP credentials (optional)
6. Update email recipient
7. Activate workflow

---

## Prerequisites

### Before Importing

1. **PostgreSQL Credentials**:
   - Host: `localhost` (or `host.docker.internal` from Docker)
   - Port: `5432`
   - Database: `aya_rag`
   - User: `postgres`
   - Password: `Power$$336633$$`

2. **SMTP Credentials** (for daily audit):
   - Configure in n8n credentials section
   - Required only for email reports

3. **File Paths**:
   - Verify `/Users/arthurdell/AYA/services/code_validator_n8n.py` exists
   - Update paths in workflows if needed

---

## Workflow Configuration

### After Import

1. **Configure Credentials**:
   - Set PostgreSQL connection in each workflow
   - Set SMTP connection for daily audit (optional)

2. **Update Email Recipient**:
   - Edit "Send Email Report" node
   - Change `arthur@aya.local` to your email

3. **Adjust File Paths** (if needed):
   - Verify code validator script path
   - Update if AYA is in different location

4. **Test Workflows**:
   - Run main validation workflow manually
   - Test webhook endpoint
   - Verify database logging

---

## Testing

### Test Main Validation Workflow

```bash
# Test webhook endpoint
curl -X POST http://localhost:5678/webhook/code-validate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(): print(\"Hello\")",
    "agent_name": "test"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "validation_id": "...",
  "enforcement_action": "pass",
  "issues_detected": 0,
  ...
}
```

### Verify Database Logging

```sql
SELECT 
    validation_id,
    filename,
    agent_name,
    enforcement_action,
    validation_time
FROM code_validations
ORDER BY validation_time DESC
LIMIT 5;
```

---

## Troubleshooting

### Workflow Not Executing

1. **Check Activation**: Ensure workflow is activated in n8n UI
2. **Check Logs**: View execution logs in n8n UI
3. **Verify Paths**: Ensure script paths are correct
4. **Check Permissions**: Ensure n8n can execute Python scripts

### Webhook Not Responding

1. **Check Workflow**: Ensure workflow is activated
2. **Check URL**: Verify webhook URL is correct
3. **Check Port**: Ensure n8n is running on port 5678
4. **Test Locally**: Try `curl` command from same machine

### Database Connection Failed

1. **Check Credentials**: Verify PostgreSQL credentials
2. **Check Connection**: Test connection from n8n container
3. **Check Host**: Use `host.docker.internal` if n8n is in Docker
4. **Check Tables**: Verify tables exist in database

---

## Workflow Modifications

### Adjust Batch Size

Edit "Set Batch Size" node in file watcher workflow:
- Change `batch_size` from 8 to desired value
- Match your LM Studio capacity

### Change Schedule

Edit schedule trigger nodes:
- File watcher: Change from 5 minutes to desired interval
- Daily audit: Change cron expression for different time

### Add Notifications

Add Slack/Discord nodes after validation:
- Configure webhook URLs
- Format messages from validation results
- Add filters for CRITICAL issues only

---

## Summary

✅ **3 Workflows Ready for Import**  
✅ **All Workflows Configured for 80B MLX Model**  
✅ **Database Logging Included**  
✅ **Enforcement Decisions Implemented**  

**Import these workflows into n8n to complete the automated code validation system!**

