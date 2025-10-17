# BETA Directory Structure - CRITICAL REFERENCE

**Date**: October 16, 2025  
**Purpose**: Document correct BETA paths to prevent production errors  
**Status**: VERIFIED

---

## 🔴 BETA HAS TWO GLADIATOR LOCATIONS

### **Location 1: GitHub Repository Clone**
```
Path: /Users/arthurdell/GLADIATOR/
Purpose: GitHub runner installation files only
Contents:
├── runners/
│   ├── install-runner.sh
│   ├── launchd/*.plist
│   └── README.md
└── datasets/ (empty placeholder)

Size: ~50KB (just installer files)
Created: rsync transfer from ALPHA
NOT the main project directory
```

### **Location 2: ACTUAL GLADIATOR PROJECT DATA** ⭐
```
Path: /Volumes/DATA/GLADIATOR/
Purpose: Real GLADIATOR project work directory
Contents:
├── attack_patterns/iteration_001/    ← 3,872 attack JSON files
├── armed_exploits/                   ← 1,421 exploit patterns
├── Qwen/                             ← Qwen3-14B model (validated @ 42.5 tok/s)
├── scripts/                          ← Generation scripts
├── variant_database/                 ← 32 CVE templates
├── logs/
└── ... (complete project structure)

Size: 53GB
Docker mount: /Volumes/DATA/GLADIATOR → /gladiator/data (inside red_combat)
THIS IS THE REAL WORKING DIRECTORY
```

---

## Docker Container Mounts

### **red_combat (BETA)**:
```bash
Mount: /Volumes/DATA/GLADIATOR → /gladiator/data

Inside container paths:
├── /gladiator/data/attack_patterns/iteration_001/
├── /gladiator/data/armed_exploits/
├── /gladiator/data/Qwen/
└── /gladiator/data/scripts/
```

**To access attack patterns in workflows:**
```bash
# WRONG (doesn't exist):
/Users/arthurdell/GLADIATOR/attack_patterns/

# CORRECT (actual data):
/Volumes/DATA/GLADIATOR/attack_patterns/

# Inside red_combat container:
docker exec red_combat ls /gladiator/data/attack_patterns/iteration_001/
```

---

## GitHub Actions Runner on BETA

**Runner Location**: `/Users/runner/actions-runner/`  
**Working Directory**: `/Users/runner/actions-runner/_work/`  
**Service**: `com.github.actions.runner.beta`  
**Status**: ✅ LISTENING FOR JOBS

**Access to GLADIATOR Data**:
- Runner executes as user: `runner`
- Can access: `/Volumes/DATA/GLADIATOR/` (if permissions allow)
- Via Docker: `docker exec red_combat <command>`

---

## Correct Workflow Paths for BETA

### **Generate Dataset (BETA)**:
```yaml
jobs:
  generate:
    runs-on: [self-hosted, macOS, arm64, beta, studio]
    steps:
      - name: Generate patterns
        run: |
          # CORRECT: Use Docker container with mounted volume
          docker exec red_combat python3 << 'EOF'
          from pathlib import Path
          ATTACK_DIR = Path("/gladiator/data/attack_patterns/iteration_001")
          # ... rest of script
          EOF
          
          # OR access directly (if permissions allow)
          cd /Volumes/DATA/GLADIATOR/attack_patterns/iteration_001
          python3 generate.py
```

### **Transfer to ALPHA**:
```yaml
- name: Transfer
  run: |
    # CORRECT source path
    rsync -avz /Volumes/DATA/GLADIATOR/reality_check_1000.json \
      alpha.local:/Users/arthurdell/GLADIATOR/datasets/
```

---

## Key Takeaways

**CRITICAL**:
1. `/Volumes/DATA/GLADIATOR/` = **REAL project data** on BETA (53GB)
2. `/Users/arthurdell/GLADIATOR/` = GitHub repo clone (just runner installer files)
3. Docker red_combat sees data at `/gladiator/data/` (mounted from /Volumes/DATA/GLADIATOR)
4. Always use `/Volumes/DATA/GLADIATOR/` in workflows/scripts on BETA
5. Always verify paths before executing commands in production

**NEVER ASSUME PATHS ARE THE SAME ACROSS SYSTEMS**

---

## Directory Structure Summary

```
BETA System:
│
├── /Users/arthurdell/GLADIATOR/          ← GitHub repo (runner installer)
│   └── runners/
│
├── /Volumes/DATA/GLADIATOR/              ← ACTUAL PROJECT (53GB)
│   ├── attack_patterns/
│   ├── Qwen/
│   └── scripts/
│
└── /Users/runner/actions-runner/         ← GitHub Actions runner
    └── _work/                            ← Temporary workflow files
```

---

**Version**: 1.0  
**Last Updated**: October 16, 2025  
**Status**: CRITICAL REFERENCE - READ BEFORE ANY BETA OPERATIONS

