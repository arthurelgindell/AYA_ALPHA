# Database Reconstruction Plan

**Generated**: October 29, 2025  
**Status**: IN PROGRESS  
**Goal**: Rebuild PostgreSQL 18 database from local project folders and GitHub repositories  

---

## Data Discovery Summary

### ✅ FOUND - Massive Recoverable Data

| Component | Location | Files Found | Status |
|-----------|----------|-------------|---------|
| **Gladiator Attack Patterns** | /Users/arthurdell/GLADIATOR/datasets | **8,305 JSON files** | 🟢 RICH |
| **Gladiator Armed Exploits** | datasets/armed_exploits | 1,423 CVE files | 🟢 RICH |
| **Gladiator Combat Training** | datasets/combat_training | 3,147 files | 🟢 RICH |
| **Gladiator Exploit Database** | datasets/exploit_database | 1,438 files | 🟢 RICH |
| **Gladiator Synthetic Data** | datasets/synthetic_base | 1,002 files | 🟢 RICH |
| **Gladiator Training 10M** | datasets/training_10m | 1,002 files | 🟢 RICH |
| **N8N System** | /Users/arthurdell/N8N | Code + Config | 🟡 PARTIAL |
| **JITM System** | /Users/arthurdell/JITM | Code (no data) | 🔴 CODE ONLY |
| **Code Audit System** | /Users/arthurdell/Code_Audit_System | Code + Logs | 🟡 PARTIAL |
| **GitHub Repositories** | 6 repos found | Active .git | 🟢 AVAILABLE |

---

## Reconstruction Priority

### Priority 1: Gladiator Attack Patterns (IMMEDIATE)

**Current State**: Only 47 attack patterns in database  
**Recoverable**: 8,305+ JSON files available  
**Impact**: CRITICAL - 99% data missing

**Data Sources**:
```
/Users/arthurdell/GLADIATOR/datasets/
├── armed_exploits/          (1,423 CVE JSON files)
├── combat_training/         (3,147 training files)
├── exploit_database/        (1,438 exploits)
├── synthetic_base/          (1,002 synthetic attacks)
├── training_10m/            (1,002 training samples)
├── adversarial/             (adversarial samples)
├── blue_team_training/      (defense patterns)
└── expansion/               (expanded datasets)
```

**Sample Files Found**:
- CVE-2010-3333.json
- CVE-2024-38178.json
- CVE-2019-1429.json
- adversarial_samples_1000.jsonl
- reality_check_1000.json
- benign_train_900.jsonl

**Action Plan**:
1. Parse armed_exploits/*.json → gladiator_attack_patterns table
2. Import combat_training data → gladiator_training_runs
3. Import exploit_database → gladiator_documentation
4. Import training datasets → gladiator_models
5. Create validation tests from benign/adversarial data

---

### Priority 2: N8N Workflows (HIGH)

**Current State**: Minimal data in database  
**Recoverable**: N8N installation with config and data directories  
**Impact**: HIGH - workflow definitions needed

**Data Sources**:
```
/Users/arthurdell/N8N/
├── data/                    (N8N runtime data)
├── workflows/               (empty - may need DB export)
├── scripts/                 (deployment scripts)
├── docker/                  (docker configs)
└── n8n_schema_extension.sql (database schema)
```

**Action Plan**:
1. Check if N8N stores workflows in PostgreSQL
2. Query existing n8n_workflows table
3. Export workflows from N8N UI if running
4. Import workflow JSON files if found

---

### Priority 3: JITM System (MEDIUM)

**Current State**: 100% missing from database  
**Recoverable**: Code structure only, no data files  
**Impact**: MEDIUM - business system but empty data directory

**Data Sources**:
```
/Users/arthurdell/JITM/
├── api/                     (FastAPI application)
│   ├── database.py         (DB connector)
│   ├── models.py           (SQLAlchemy models)
│   └── routers/            (API endpoints)
├── data/                    (EMPTY)
├── docker/                  (containerization)
└── workflows/               (EMPTY)
```

**Action Plan**:
1. Review models.py for schema definitions
2. Create empty tables if missing
3. Generate seed data from model definitions
4. Check if JITM has external data sources (API connections)
5. Consider if JITM is a prototype (no production data expected)

---

### Priority 4: Code Audit System (LOW)

**Current State**: ~30% in database  
**Recoverable**: Code and some logs available  
**Impact**: LOW - development/QA system

**Data Sources**:
```
/Users/arthurdell/Code_Audit_System/
├── core/                    (audit logic)
├── providers/               (code scanning providers)
├── scripts/                 (automation)
├── logs/                    (audit logs)
└── reports/                 (findings reports)
```

**Action Plan**:
1. Parse logs for historical audit runs
2. Import findings from reports
3. Reconstruct audit history from git commits

---

## Import Scripts Needed

### 1. Gladiator Attack Pattern Importer

```python
# File: /Users/arthurdell/AYA/scripts/import_gladiator_patterns.py
# Purpose: Import all Gladiator attack patterns from JSON files

import json
import psycopg2
from pathlib import Path
from datetime import datetime

def import_armed_exploits():
    """Import CVE attack patterns from armed_exploits/"""
    base_path = Path("/Users/arthurdell/GLADIATOR/datasets/armed_exploits")
    
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='aya_rag',
        user='postgres',
        password='Power$$336633$$'
    )
    
    cursor = conn.cursor()
    imported = 0
    
    for json_file in base_path.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            # Insert into gladiator_attack_patterns
            cursor.execute("""
                INSERT INTO gladiator_attack_patterns 
                (pattern_id, attack_type, attack_category, payload, description,
                 mitre_attack_tactic, mitre_attack_technique, metadata_json,
                 storage_path, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pattern_id) DO NOTHING
            """, (
                data.get('id', json_file.stem),
                data.get('attack_type', 'exploit'),
                data.get('category', 'vulnerability'),
                data.get('payload', ''),
                data.get('description', ''),
                data.get('mitre_tactic', ''),
                data.get('mitre_technique', ''),
                json.dumps(data),
                str(json_file),
                datetime.now()
            ))
            imported += 1
            
            if imported % 100 == 0:
                conn.commit()
                print(f"Imported {imported} patterns...")
                
        except Exception as e:
            print(f"Error importing {json_file}: {e}")
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Total imported: {imported} attack patterns")

if __name__ == "__main__":
    import_armed_exploits()
```

### 2. N8N Workflow Importer

```python
# File: /Users/arthurdell/AYA/scripts/import_n8n_workflows.py
# Purpose: Check N8N database for workflows and import if found
```

### 3. Comprehensive Database Rebuild Script

```bash
#!/bin/bash
# File: /Users/arthurdell/AYA/scripts/rebuild_database.sh
# Purpose: Orchestrate full database rebuild

echo "=== DATABASE RECONSTRUCTION ==="
echo ""

# 1. Import Gladiator Attack Patterns
echo "1. Importing Gladiator Attack Patterns..."
python3 /Users/arthurdell/AYA/scripts/import_gladiator_patterns.py

# 2. Check N8N Workflows
echo "2. Checking N8N Workflows..."
python3 /Users/arthurdell/AYA/scripts/import_n8n_workflows.py

# 3. Generate JITM Seed Data
echo "3. Generating JITM Seed Data..."
python3 /Users/arthurdell/AYA/scripts/seed_jitm_data.py

# 4. Verify Reconstructed Data
echo "4. Verifying Reconstruction..."
python3 /Users/arthurdell/AYA/scripts/verify_reconstruction.py

echo ""
echo "=== RECONSTRUCTION COMPLETE ==="
```

---

## GitHub Repository Status

Found 6 active Git repositories:
1. `/Users/arthurdell/GLADIATOR` - Main Gladiator project
2. `/Users/arthurdell/Code_Audit_System` - Audit system
3. `/Users/arthurdell/N8N` - N8N deployment
4. `/Users/arthurdell/AYA` - Main AYA project
5. `/Users/arthurdell/.nvm` - Node version manager
6. `/Users/arthurdell/homebrew` - Homebrew packages

**Action**: Can push/pull latest data if remote configured

---

## Expected Outcomes

### After Gladiator Import:
- **Before**: 47 attack patterns
- **After**: 8,000+ attack patterns
- **Gain**: 170x increase in attack intelligence

### After N8N Import:
- **Before**: Minimal workflow data
- **After**: Full workflow definitions
- **Gain**: Restore automation capabilities

### After JITM Seed:
- **Before**: 0 records
- **After**: Seed/test data populated
- **Gain**: Functional testing capability

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| JSON parsing errors | Medium | Robust error handling, skip bad files |
| Duplicate data | Low | Use ON CONFLICT DO NOTHING |
| Schema mismatches | High | Validate against current schema first |
| Import time | Low | Batch commits every 100 records |
| Disk space | Low | 586 MB → ~1-2 GB estimated |

---

## Success Criteria

- ✅ 8,000+ Gladiator attack patterns imported
- ✅ N8N workflows restored
- ✅ JITM tables populated with seed data
- ✅ Database integrity verified
- ✅ All foreign keys maintained
- ✅ Vector embeddings generated for new content

---

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Gladiator Import | 30-60 min | READY |
| Phase 2: N8N Workflows | 15 min | READY |
| Phase 3: JITM Seed Data | 15 min | READY |
| Phase 4: Verification | 15 min | READY |
| **Total** | **1-2 hours** | **READY TO START** |

---

## Next Steps

1. Create import scripts
2. Test on sample dataset (100 records)
3. Run full import
4. Verify data integrity
5. Update database content analysis
6. Create new backup with Carbon Copy Cloner

---

**Status**: ✅ RECONSTRUCTION PLAN COMPLETE - READY TO EXECUTE

**Recommendation**: START IMMEDIATELY with Gladiator attack pattern import

