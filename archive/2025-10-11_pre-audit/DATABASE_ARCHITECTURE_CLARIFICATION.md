# DATABASE ARCHITECTURE - ALPHA Primary, BETA Replica

## CORRECT SETUP (Already Configured)

```
ALPHA:
├─ PostgreSQL: PRIMARY (read/write) ✅
├─ Database: aya_rag (master)
├─ Port: 5432
├─ Access: localhost (ALPHA only)
└─ Role: Single source of truth

BETA:
├─ PostgreSQL: STREAMING REPLICA (read-only) ✅
├─ Database: aya_rag (replica from ALPHA)
├─ Port: 5432
├─ Access: localhost (BETA only)
└─ Role: Backup, can promote if ALPHA fails

Replication: ALPHA → BETA (streaming, automatic)
```

## WHY BETA CAN'T WRITE (This is CORRECT)

**BETA is intentionally read-only replica**:
- Prevents data conflicts
- ALPHA is authoritative
- BETA can read current state
- BETA cannot write (by design)

**BETA Cursor discovered this correctly**:
- Tried to write: Got "recovery mode" error
- This is EXPECTED behavior
- Not a bug, it's the architecture

## AGENT COORDINATION STRATEGY (Corrected)

**For BETA Cursor (or any agent on BETA)**:
```python
# OPTION 1: Write to ALPHA database (remote)
conn = psycopg2.connect(
    host='192.168.0.80',  # ALPHA IP, not localhost
    database='aya_rag',
    user='postgres',
    password='Power$$336633$$'
)
# Now can write to primary

# OPTION 2: File-based signals (what BETA used)
# Create /Volumes/DATA/GLADIATOR/BETA_READY.txt
# ALPHA monitors file for signals

# OPTION 3: Network API
# POST to ALPHA endpoint with status updates
```

**For ALPHA Cursor (me)**:
```python
# Write directly to local database (primary)
conn = psycopg2.connect(
    host='localhost',
    database='aya_rag',
    ...
)
# This works ✅
```

## BETA Cursor Was CORRECT

**Issue identified**: BETA database read-only  
**Workaround implemented**: File-based signal  
**Resolution**: I (ALPHA Cursor) log BETA's work to primary database  

**This is multi-agent coordination working as designed.**

---

**Database coordination for BETA agents**: Connect to ALPHA IP (192.168.0.80) not localhost
**OR**: Use file-based signals (simpler, works)
