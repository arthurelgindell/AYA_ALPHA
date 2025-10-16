# GLADIATOR DATABASE DEPLOYMENT GUIDE
**Date**: October 10, 2025  
**Target Database**: aya_rag (PostgreSQL 18.0)  
**Integration**: Extends existing AYA infrastructure schema  
**Status**: READY FOR DEPLOYMENT

---

## EXECUTIVE SUMMARY

**Purpose**: Create GLADIATOR reference database that tracks complete project state in real-time.

**Strategy**:
- Documentation is fallback
- Database is single source of truth
- Aligned with AYA standards (JSONB metadata, full-text search, timestamps)
- Production-grade tracking for 14-week Phase 0

**Tables Created**: 11 core tables + 3 views
**Initial Data**: Models, validation results, milestones, current project state

---

## ARCHITECTURE ALIGNMENT WITH AYA

### AYA Database Pattern (Existing)
```
aya_rag database:
├─ Infrastructure Tables (11 tables)
│  ├─ system_nodes - Hardware specs
│  ├─ network_interfaces - Network config
│  ├─ software_versions - Software inventory
│  ├─ services - Running services
│  └─ ... (performance, replication, etc.)
│
├─ Documentation Tables (7 tables)
│  ├─ postgresql_documentation (1,143 docs)
│  ├─ docker_documentation (2,000 docs)
│  └─ ... (7,441 docs total)
│
└─ Core RAG Tables (2 tables)
   ├─ documents - User documents
   └─ chunks - Vector embeddings
```

### GLADIATOR Extension (New)
```
aya_rag database (EXTENDED):
├─ EXISTING AYA TABLES (unchanged)
│
└─ GLADIATOR Tables (11 new tables) ✨
   ├─ gladiator_documentation - Project docs with full-text search
   ├─ gladiator_models - Model registry
   ├─ gladiator_training_runs - Training sessions
   ├─ gladiator_training_metrics - Time-series metrics
   ├─ gladiator_attack_patterns - Red Team output (10M+ patterns)
   ├─ gladiator_attack_generation_stats - Daily generation stats
   ├─ gladiator_validation_tests - Gate validation results
   ├─ gladiator_phase_milestones - Phase 0 timeline
   ├─ gladiator_project_state - Current state dashboard
   ├─ gladiator_hardware_performance - Training hardware metrics
   └─ gladiator_change_log - Complete audit trail
```

### Standards Compliance
```
✅ JSONB metadata (consistent with AYA)
✅ Full-text search (GIN indexes)
✅ Timestamp tracking (created_at, updated_at)
✅ Foreign keys to AYA tables (system_nodes)
✅ Consistent naming (gladiator_* prefix)
✅ Audit triggers (updated_at auto-update)
✅ Views for dashboards
```

---

## PRE-DEPLOYMENT CHECKLIST

### 1. Database Access
- [ ] PostgreSQL 18.0 running on ALPHA
- [ ] aya_rag database exists
- [ ] User has CREATE TABLE permissions
- [ ] GIN extension available (for full-text search)

### 2. Verify AYA Schema
```bash
# Check if AYA infrastructure tables exist
psql -h localhost -U postgres -d aya_rag -c "\dt system_nodes"

# Expected: Table exists with infrastructure data
```

### 3. Backup Existing Database
```bash
# MANDATORY before schema changes
pg_dump -h localhost -U postgres -d aya_rag -Fc -f ~/aya_rag_backup_$(date +%Y%m%d).dump

# Verify backup
ls -lh ~/aya_rag_backup_*.dump
```

---

## DEPLOYMENT PROCEDURE

### STEP 1: Deploy Schema (5 minutes)

```bash
cd /Users/arthurdell/GLADIATOR

# Execute schema creation
psql -h localhost -U postgres -d aya_rag -f gladiator_schema.sql

# Expected output:
# BEGIN
# CREATE TABLE (11 times)
# CREATE INDEX (many)
# CREATE VIEW (3 times)
# CREATE FUNCTION
# CREATE TRIGGER (4 times)
# INSERT (2 initial records)
# COMMIT
```

**Verification**:
```bash
# Check tables created
psql -h localhost -U postgres -d aya_rag -c "\dt gladiator_*"

# Expected: 11 tables listed
# gladiator_documentation
# gladiator_models
# gladiator_training_runs
# gladiator_training_metrics
# gladiator_attack_patterns
# gladiator_attack_generation_stats
# gladiator_validation_tests
# gladiator_phase_milestones
# gladiator_project_state
# gladiator_hardware_performance
# gladiator_change_log
```

### STEP 2: Populate Initial Data (2 minutes)

```bash
# Execute population script
psql -h localhost -U postgres -d aya_rag -f populate_gladiator_db.sql

# Expected output:
# BEGIN
# INSERT ... (multiple inserts for models, tests, milestones)
# UPDATE ... (project state)
# SELECT (verification queries with results)
# COMMIT
```

**Verification Queries**:
```sql
-- Check current project status
SELECT * FROM gladiator_status_dashboard;

-- Expected:
-- current_phase: pre_flight
-- phase_0_progress_percentage: 5
-- foundation_model_validated: TRUE
-- gates_passed: 0
-- gates_total: 7

-- Check models registered
SELECT model_name, model_type, status, deployed_on 
FROM gladiator_models;

-- Expected: 4 models (1 validated, 3 planned)

-- Check validation tests
SELECT test_name, test_result, go_no_go_decision 
FROM gladiator_validation_tests;

-- Expected: 7 tests, all PASS, all GO decisions

-- Check milestones
SELECT phase, week_number, milestone_name, status 
FROM gladiator_phase_milestones 
ORDER BY week_number;

-- Expected: 11 milestones from week -15 to week 0
```

---

## POST-DEPLOYMENT VERIFICATION

### Test 1: Query Current Status
```sql
SELECT 
    current_phase,
    phase_0_progress_percentage,
    total_attack_patterns_generated,
    foundation_model_validated,
    critical_blockers
FROM gladiator_project_state
WHERE is_current = TRUE;
```

**Expected**:
```
current_phase: pre_flight
phase_0_progress_percentage: 5
total_attack_patterns_generated: 0
foundation_model_validated: TRUE
critical_blockers: 0
```

### Test 2: Check Model Registry
```sql
SELECT 
    model_name,
    model_type,
    deployed_on,
    status,
    validation_notes
FROM gladiator_models
WHERE status = 'validated';
```

**Expected**: 1 row (foundation-sec-8b-instruct-int8)

### Test 3: Validation Tests
```sql
SELECT 
    COUNT(*) as total_tests,
    SUM(CASE WHEN test_result = 'PASS' THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN go_no_go_decision = 'GO' THEN 1 ELSE 0 END) as go_decisions
FROM gladiator_validation_tests;
```

**Expected**: total_tests=7, passed=7, go_decisions=7

### Test 4: Full-Text Search
```sql
-- Test documentation search
SELECT doc_name, doc_type 
FROM gladiator_documentation 
WHERE to_tsvector('english', content) @@ to_tsquery('validation & model');
```

**Expected**: Returns documentation containing "validation" and "model"

### Test 5: Integration with AYA
```sql
-- Verify foreign key relationship
SELECT 
    sn.node_name,
    sn.ram_gb,
    COUNT(gm.id) as models_deployed
FROM system_nodes sn
LEFT JOIN gladiator_models gm ON gm.deployed_on = sn.node_name
GROUP BY sn.node_name, sn.ram_gb;
```

**Expected**:
```
ALPHA | 512 | 1 (foundation model)
BETA  | 256 | 3 (red team models - planned)
```

---

## DATABASE USAGE PATTERNS

### Pattern 1: Update Project State
```sql
-- When milestone completes
UPDATE gladiator_phase_milestones 
SET 
    status = 'completed',
    actual_end_date = CURRENT_DATE,
    completion_percentage = 100
WHERE week_number = -15;  -- Pre-flight milestone

-- Auto-update project state
UPDATE gladiator_project_state
SET 
    phase_0_progress_percentage = 10,
    gates_passed = gates_passed + 1,
    last_gate_passed = 'gate_0'
WHERE is_current = TRUE;
```

### Pattern 2: Log Training Run
```sql
-- Start training run
INSERT INTO gladiator_training_runs (
    run_name,
    run_type,
    phase,
    base_model_id,
    target_model_name,
    training_dataset_size,
    batch_size,
    learning_rate,
    trained_on,
    status,
    started_at
) VALUES (
    'reality_check_1k_samples',
    'reality_check',
    'phase_0',
    (SELECT id FROM gladiator_models WHERE model_name = 'foundation-sec-8b-instruct-int8'),
    'foundation-sec-8b-finetuned-reality',
    1000,
    32,
    0.0001,
    'ALPHA',
    'running',
    NOW()
) RETURNING id;

-- Log metrics during training
INSERT INTO gladiator_training_metrics (
    training_run_id,
    epoch,
    step,
    training_loss,
    validation_accuracy,
    gpu_utilization,
    ram_usage_gb
) VALUES (
    <run_id>,
    1,
    50,
    0.043,
    88.5,
    94.0,
    450.0
);
```

### Pattern 3: Track Attack Generation
```sql
-- Daily stats for Red Team
INSERT INTO gladiator_attack_generation_stats (
    stat_date,
    total_patterns_generated,
    by_category,
    patterns_per_hour,
    total_storage_gb
) VALUES (
    CURRENT_DATE,
    250000,
    '{"network": 50000, "web": 75000, "system": 50000, "social": 25000, "apt": 50000}'::jsonb,
    10416.7,
    8.5
);

-- Individual attack pattern
INSERT INTO gladiator_attack_patterns (
    pattern_id,
    attack_type,
    attack_category,
    complexity_level,
    payload,
    generated_by_model_id,
    storage_path
) VALUES (
    'attack_001234',
    'sql_injection',
    'web',
    7,
    '{"payload": "'' OR 1=1 --", "target": "login_form"}',
    (SELECT id FROM gladiator_models WHERE model_name = 'TinyLlama-1.1B-Chat-v1.0-4bit'),
    '/Volumes/DATA/GLADIATOR/attack_patterns/web/sql_injection/attack_001234.json'
);
```

### Pattern 4: Dashboard Query
```sql
-- Real-time project dashboard
SELECT 
    ps.current_phase,
    ps.phase_0_progress_percentage,
    ps.total_attack_patterns_generated || ' / ' || ps.attack_patterns_target as attack_progress,
    ps.current_model_accuracy || '% (target: ' || ps.target_accuracy || '%)' as model_accuracy,
    ps.gates_passed || ' / ' || ps.gates_total as gates_progress,
    ps.critical_blockers || ' blockers, ' || ps.major_risks || ' risks' as health,
    CASE 
        WHEN ps.production_ready THEN '✅ READY'
        WHEN ps.phase_0_progress_percentage >= 50 THEN '🟡 IN PROGRESS'
        ELSE '🔴 EARLY STAGE'
    END as status
FROM gladiator_project_state ps
WHERE ps.is_current = TRUE;
```

---

## INTEGRATION WITH EXTERNAL TOOLS

### Grafana Dashboard (Future)
```sql
-- Time-series metrics for visualization
SELECT 
    measured_at,
    training_loss,
    validation_accuracy,
    gpu_utilization
FROM gladiator_training_metrics
WHERE training_run_id = <run_id>
ORDER BY measured_at DESC;
```

### Python Integration
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="aya_rag",
    user="postgres"
)

# Get current status
cursor = conn.cursor()
cursor.execute("SELECT * FROM gladiator_status_dashboard")
status = cursor.fetchone()
print(f"Phase: {status[0]}, Progress: {status[2]}%")

# Log training metric
cursor.execute("""
    INSERT INTO gladiator_training_metrics 
    (training_run_id, epoch, step, training_loss, validation_accuracy)
    VALUES (%s, %s, %s, %s, %s)
""", (run_id, epoch, step, loss, accuracy))
conn.commit()
```

---

## MAINTENANCE & BACKUPS

### Daily Backup
```bash
# Add to cron: daily backup at 3 AM
0 3 * * * pg_dump -h localhost -U postgres -d aya_rag -Fc -f ~/backups/aya_rag_$(date +\%Y\%m\%d).dump
```

### Weekly Cleanup
```sql
-- Remove old training metrics (keep last 30 days)
DELETE FROM gladiator_training_metrics
WHERE measured_at < NOW() - INTERVAL '30 days'
AND training_run_id IN (
    SELECT id FROM gladiator_training_runs 
    WHERE status = 'completed'
);

-- Vacuum after cleanup
VACUUM ANALYZE gladiator_training_metrics;
```

### Monitoring Queries
```sql
-- Check database size
SELECT 
    pg_size_pretty(pg_database_size('aya_rag')) as total_size,
    pg_size_pretty(
        SUM(pg_total_relation_size(quote_ident(tablename)::text))
    ) as gladiator_tables_size
FROM pg_tables
WHERE tablename LIKE 'gladiator_%';

-- Check recent activity
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    last_autovacuum
FROM pg_stat_user_tables
WHERE tablename LIKE 'gladiator_%'
ORDER BY n_tup_ins + n_tup_upd DESC;
```

---

## TROUBLESHOOTING

### Issue: Schema creation fails
**Symptom**: "permission denied for database aya_rag"
**Solution**:
```bash
# Grant permissions
psql -h localhost -U postgres -c "GRANT ALL ON DATABASE aya_rag TO arthurdell;"
```

### Issue: Foreign key constraint fails
**Symptom**: "foreign key constraint ... violates foreign key"
**Solution**: Ensure AYA system_nodes table has ALPHA and BETA entries
```sql
SELECT node_name FROM system_nodes;
-- Should show: ALPHA, BETA
```

### Issue: Full-text search not working
**Symptom**: "operator does not exist: tsvector @@ tsquery"
**Solution**: Ensure pg_trgm extension is enabled
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Issue: Views not updating
**Symptom**: gladiator_status_dashboard shows old data
**Solution**: Views are real-time, check underlying tables
```sql
REFRESH MATERIALIZED VIEW IF EXISTS gladiator_status_dashboard;
-- Note: Views in this schema are NOT materialized, should update automatically
```

---

## ROLLBACK PROCEDURE

If deployment fails or needs to be undone:

```sql
BEGIN;

-- Drop GLADIATOR tables (in reverse dependency order)
DROP TABLE IF EXISTS gladiator_change_log CASCADE;
DROP TABLE IF EXISTS gladiator_hardware_performance CASCADE;
DROP TABLE IF EXISTS gladiator_attack_generation_stats CASCADE;
DROP TABLE IF EXISTS gladiator_attack_patterns CASCADE;
DROP TABLE IF EXISTS gladiator_training_metrics CASCADE;
DROP TABLE IF EXISTS gladiator_training_runs CASCADE;
DROP TABLE IF EXISTS gladiator_validation_tests CASCADE;
DROP TABLE IF EXISTS gladiator_phase_milestones CASCADE;
DROP TABLE IF EXISTS gladiator_project_state CASCADE;
DROP TABLE IF EXISTS gladiator_models CASCADE;
DROP TABLE IF EXISTS gladiator_documentation CASCADE;

-- Drop views
DROP VIEW IF EXISTS gladiator_status_dashboard CASCADE;
DROP VIEW IF EXISTS gladiator_latest_validations CASCADE;
DROP VIEW IF EXISTS gladiator_active_training CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

COMMIT;

-- Restore from backup if needed
-- pg_restore -h localhost -U postgres -d aya_rag ~/aya_rag_backup_YYYYMMDD.dump
```

---

## SUCCESS CRITERIA

**Deployment Successful When**:
- ✅ All 11 tables created
- ✅ All 3 views functional
- ✅ 4 models registered (1 validated, 3 planned)
- ✅ 7 validation tests logged (all PASS)
- ✅ 11 milestones defined
- ✅ Project state shows current status
- ✅ Full-text search working
- ✅ Integration with AYA tables verified
- ✅ No errors in PostgreSQL logs

---

## NEXT STEPS AFTER DEPLOYMENT

1. **Continuous Updates**: Update `gladiator_project_state` as project progresses
2. **Log Training**: Use `gladiator_training_runs` and `gladiator_training_metrics` during Phase 0
3. **Track Attack Generation**: Populate `gladiator_attack_patterns` as BETA generates attacks
4. **Validation Gates**: Log results in `gladiator_validation_tests` at each gate
5. **Build Dashboards**: Create queries/views for real-time monitoring

---

## CONTACT & SUPPORT

**Database Schema**: /Users/arthurdell/GLADIATOR/gladiator_schema.sql  
**Population Script**: /Users/arthurdell/GLADIATOR/populate_gladiator_db.sql  
**This Guide**: /Users/arthurdell/GLADIATOR/GLADIATOR_DATABASE_DEPLOYMENT.md

**Questions**: Refer to AYA documentation pattern for consistency

---

**END OF DEPLOYMENT GUIDE**

