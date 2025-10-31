# AYA Bulletproof Architecture - Deployment Guide

**Date:** October 31, 2025  
**Version:** 1.0  
**System:** ALPHA (192.168.0.80) → BETA (192.168.0.20) Relay Coordination  

---

## Overview

The AYA Bulletproof Architecture provides:
- **Immutable Audit Trail**: Blockchain-style append-only event log
- **Milestone Gates**: Semi-autonomous operation with manual approval points
- **4-Phase Verification**: Prime Directives enforcement via database
- **ALPHA↔BETA Relay Cycles**: Recursive self-improvement through role swapping

---

## Deployment Summary

### What Was Deployed

1. **Database Schema** (8 tables)
   - `aya_bulletproof_audit` - Immutable event log with hash chaining
   - `aya_relay_cycles` - Relay cycle state machine
   - `aya_verification_chain` - Bulletproof verification checkpoints
   - `aya_system_operations` - Cross-system operation tracking
   - `aya_gamma_workloads` - Future GAMMA subordination control
   - `aya_system_health` - System health monitoring
   - `aya_relay_enhancements` - Enhancement tracking
   - `aya_milestone_approvals` - Approval queue

2. **Orchestration Functions**
   - `initiate_relay_cycle()` - Start new cycles
   - `transition_relay_phase()` - Phase transitions with gates
   - `request_milestone_approval()` - Request approvals
   - `grant_milestone_approval()` - Grant approvals
   - `record_verification_checkpoint()` - Record verifications
   - `record_relay_enhancement()` - Track improvements
   - `relay_cycle_fully_verified()` - Verification checker
   - `check_stale_systems()` - Health monitoring

3. **LISTEN/NOTIFY Triggers** (8 triggers)
   - Real-time event notifications via PostgreSQL
   - Relay phase transitions
   - Verification checkpoints
   - Milestone approvals
   - System health changes

4. **Integration Views** (8 views)
   - `aya_platform_status` - Live system status
   - `aya_pending_approvals` - Approval dashboard
   - `aya_relay_performance` - Historical metrics
   - `aya_system_health_dashboard` - Health monitoring
   - `aya_active_relay_details` - Active cycle details
   - `aya_audit_summary` - Audit trail summary
   - `aya_enhancement_impact` - Enhancement analysis
   - `aya_operations_status` - Cross-system operations

5. **MCP Coordinator Server**
   - Location: `/Users/arthurdell/AYA/mcp_servers/aya-bulletproof/`
   - FastMCP-based server for Claude Desktop integration
   - 10 MCP tools for relay coordination
   - PostgreSQL LISTEN/NOTIFY event handling

---

## Database Connection

```bash
# Connect to aya_rag database
PGPASSWORD='Power$$336633$$' psql -h localhost -p 5432 -U postgres -d aya_rag

# View bulletproof tables
\dt aya_*

# View bulletproof functions
\df *relay*
```

---

## MCP Tools Reference

### 1. initiate_relay_cycle
Start a new ALPHA↔BETA relay cycle.

**Parameters:**
- `source_node` (str): 'ALPHA' or 'BETA'
- `target_node` (str): 'ALPHA' or 'BETA'
- `enhancement_goals` (str): JSON string of goals

**Example:**
```python
result = await initiate_relay_cycle(
    source_node="ALPHA",
    target_node="BETA",
    enhancement_goals='{"optimize": "performance", "target": "agent_turbo"}'
)
```

### 2. transition_relay_phase
Move to the next phase in the relay cycle.

**Parameters:**
- `cycle_id` (str): UUID of the cycle
- `next_phase` (str): ANALYZE, ENHANCE, TRANSFER, VALIDATE, or COMPLETE
- `evidence` (str): JSON string of evidence
- `skip_milestone_check` (bool): Skip approval check (default: false)

**Phase Flow:**
```
INIT → ANALYZE → ENHANCE → TRANSFER* → VALIDATE → COMPLETE*
                            ↑                        ↑
                      Milestone Gate          Milestone Gate
```

### 3. request_milestone_approval
Request manual approval for gated transitions.

**Parameters:**
- `cycle_id` (str): UUID of the cycle
- `milestone_type` (str): Type of milestone
- `description` (str): What needs approval
- `impact_analysis` (str): JSON impact analysis
- `requested_by` (str): Requester (default: "AYA")

### 4. grant_milestone_approval
Grant a pending approval.

**Parameters:**
- `approval_id` (str): UUID of the approval
- `approved_by` (str): Approver (default: "Arthur")
- `notes` (str): Optional notes

### 5. record_verification_checkpoint
Record Prime Directives verification.

**Parameters:**
- `cycle_id` (str): UUID of the cycle
- `node` (str): ALPHA or BETA
- `phase` (int): 1-4
- `phase_name` (str): Phase name
- `checkpoint` (str): Checkpoint name
- `verified` (bool): Pass/fail
- `evidence` (str): JSON evidence
- `verifier` (str): Who verified
- `method` (str): Verification method
- `requires_approval` (bool): Needs manual approval

**Required Checkpoints:**
- Phase 1: `component_health`
- Phase 2: `dependency_chain`, `integration_functional`
- Phase 3: `orchestration_operational`
- Phase 4: `user_workflow`, `failure_impact`

### 6. get_relay_status
Get relay cycle status.

**Parameters:**
- `cycle_id` (str): Optional specific cycle

**Returns:**
- Active cycles with verification status
- Pending approvals
- Current phase and metrics

### 7. get_pending_approvals
List all pending milestone approvals.

**Returns:**
- All approvals awaiting action
- Time pending
- Associated cycle information

### 8. record_relay_enhancement
Record improvements made during cycle.

**Parameters:**
- `cycle_id` (str): UUID of the cycle
- `enhancement_type` (str): Type of enhancement
- `component` (str): Component affected
- `before_state` (str): JSON before state
- `after_state` (str): JSON after state
- `metrics` (str): JSON metrics
- `applied_by` (str): Node that applied

### 9. update_system_health
Update system health metrics.

**Parameters:**
- `system_name` (str): ALPHA or BETA
- `cpu_percent` (float): CPU usage
- `memory_used_gb` (float): Memory used
- `memory_total_gb` (float): Total memory
- `disk_used_gb` (float): Disk used
- `disk_total_gb` (float): Total disk
- `metadata` (str): JSON metadata

---

## Test Relay Cycle

### Step 1: Initiate Cycle
```sql
-- Via SQL
SELECT initiate_relay_cycle('ALPHA', 'BETA', '{"test": true}'::jsonb);

-- Via MCP Tool
cycle_id = await initiate_relay_cycle(
    source_node="ALPHA",
    target_node="BETA",
    enhancement_goals='{"test": true}'
)
```

### Step 2: Verify Checkpoints
```python
# Record Phase 1 verification
await record_verification_checkpoint(
    cycle_id=cycle_id,
    node="ALPHA",
    phase=1,
    phase_name="Component Health",
    checkpoint="component_health",
    verified=True,
    evidence='{"all_systems": "operational"}'
)
```

### Step 3: Transition Through Phases
```python
# INIT → ANALYZE (automatic)
await transition_relay_phase(
    cycle_id=cycle_id,
    next_phase="ANALYZE",
    evidence='{"analysis": "complete"}'
)

# ANALYZE → ENHANCE (automatic)
await transition_relay_phase(
    cycle_id=cycle_id,
    next_phase="ENHANCE",
    evidence='{"enhancements": "designed"}'
)

# ENHANCE → TRANSFER (needs approval)
approval_id = await request_milestone_approval(
    cycle_id=cycle_id,
    milestone_type="PHASE_TRANSITION",
    description="Ready to transfer enhancements to BETA",
    impact_analysis='{"risk": "low", "benefit": "high"}'
)

# Grant approval
await grant_milestone_approval(
    approval_id=approval_id,
    approved_by="Arthur",
    notes="Approved for testing"
)

# Now transition
await transition_relay_phase(
    cycle_id=cycle_id,
    next_phase="TRANSFER",
    evidence='{"transfer": "initiated"}'
)
```

---

## Monitoring and Dashboards

### Platform Status
```sql
SELECT * FROM aya_platform_status;
```

### Active Cycles
```sql
SELECT * FROM aya_active_relay_details;
```

### Pending Approvals
```sql
SELECT * FROM aya_pending_approvals;
```

### Audit Trail
```sql
SELECT * FROM aya_bulletproof_audit 
WHERE relay_cycle_id IS NOT NULL
ORDER BY event_id DESC LIMIT 20;
```

### System Health
```sql
SELECT * FROM aya_system_health_dashboard;
```

---

## LISTEN/NOTIFY Events

### Subscribe to Events
```sql
-- In psql terminal
LISTEN aya_relay_phase;
LISTEN aya_verification;
LISTEN aya_milestone_approval;
LISTEN aya_audit_event;

-- Events will appear as:
-- Asynchronous notification "aya_relay_phase" with payload "{...}" received
```

### Available Channels
- `aya_relay_phase` - Phase transitions
- `aya_verification` - Verification checkpoints
- `aya_milestone_approval` - Approval requests
- `gamma_workload_authorized` - GAMMA authorizations
- `aya_system_health` - Health changes
- `aya_enhancement_applied` - Enhancements
- `aya_audit_event` - Critical events
- `aya_operation_status` - Operation updates

---

## Troubleshooting

### MCP Server Issues

**Server Not Starting:**
```bash
cd /Users/arthurdell/AYA/mcp_servers/aya-bulletproof
source venv/bin/activate
python coordinator.py

# Check for errors
# Common issues:
# - Database connection
# - Missing dependencies
# - Port conflicts
```

**Tools Not Available in Claude:**
1. Restart Claude Desktop
2. Check `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Verify server is in config
4. Check Claude logs: `~/Library/Logs/Claude/`

### Database Issues

**Foreign Key Errors:**
```sql
-- Check referenced tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('agent_sessions', 'n8n_workflows', 
                     'gladiator_training_runs', 'code_audit_runs');
```

**Immutable Audit Errors:**
```sql
-- Audit table allows INSERT only
-- No UPDATE or DELETE permitted
-- This is by design - audit trail is permanent
```

### Phase Transition Errors

**"Milestone Approval Required":**
- This is expected for TRANSFER and COMPLETE phases
- Use `request_milestone_approval()` first
- Then `grant_milestone_approval()`
- Finally retry the phase transition

**"Bulletproof Verification Failed":**
- All 6 required checkpoints must be verified
- Use `record_verification_checkpoint()` for each
- Check status with `relay_cycle_fully_verified(cycle_id)`

---

## Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐
│     ALPHA       │     │      BETA       │
│  Mac Studio     │◄───►│   Mac Studio    │
│ (192.168.0.80)  │     │ (192.168.0.20)  │
└────────┬────────┘     └─────────────────┘
         │
         │ MCP Protocol
         │
┌────────▼────────┐
│ Claude Desktop  │
│ + Coordinator   │
└────────┬────────┘
         │
         │ asyncpg
         │
┌────────▼────────┐     ┌─────────────────┐
│  PostgreSQL 18  │     │  Future: GAMMA  │
│   (aya_rag)     │     │  NVIDIA DGX     │
│                 │◄────┤    (Planned)    │
└─────────────────┘     └─────────────────┘
         │
         │ Integration
         │
┌────────▼───────────────────────────────┐
│          Existing Systems              │
│                                        │
│ • Agent Turbo (Orchestration)         │
│ • GLADIATOR (Red Team Platform)       │
│ • N8N (Workflow Automation)           │
│ • Code Audit (Security Analysis)      │
│ • Intelligence Scout (Knowledge)      │
└────────────────────────────────────────┘
```

---

## Prime Directives Enforcement

The system enforces AYA's Prime Directives through:

1. **Functional Reality Only**
   - All operations are real database transactions
   - No mock data or theatrical responses
   - Immutable audit trail proves actions

2. **Truth Over Comfort**
   - Milestone gates require explicit approval
   - Failures are logged and cannot be hidden
   - Verification must be complete or cycle fails

3. **Execute with Precision**
   - Database constraints enforce rules
   - Phase sequence is strictly ordered
   - No shortcuts or rule bypassing allowed

---

## Next Steps

1. **Test Full Relay Cycle**
   - Run complete ALPHA → BETA cycle
   - Verify all checkpoints
   - Measure improvement metrics

2. **Configure Automated Health Monitoring**
   - Set up periodic health updates
   - Configure alerting thresholds
   - Monitor relay performance

3. **Plan First Production Enhancement**
   - Define real improvement goals
   - Set success metrics
   - Schedule relay cycle

4. **Prepare for GAMMA Integration**
   - Schema already supports GAMMA
   - Subordination controls in place
   - Awaiting hardware delivery

---

## Support

For issues or questions:
1. Check audit trail for error details
2. Review PostgreSQL logs
3. Verify MCP server logs
4. Consult this guide

**Database:** `aya_rag` on localhost:5432  
**MCP Server:** `/Users/arthurdell/AYA/mcp_servers/aya-bulletproof/`  
**Claude Config:** `~/Library/Application Support/Claude/claude_desktop_config.json`
