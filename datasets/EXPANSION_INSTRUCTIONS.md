# GLADIATOR Dataset Expansion - Track 3 Execution Instructions

**Generated**: 2025-10-22 20:25:54
**Target**: 11,000 total samples
**Timeline**: 2-3 weeks (parallel with Week 1)

---

## EXECUTION ON BETA SYSTEM

### Prerequisites
- BETA system accessible
- red_combat container running
- LM Studio operational (http://localhost:1234)
- CVE database accessible

### Phase 1: Privilege Escalation (Week 1, Days 1-2)
**Priority**: CRITICAL (only 62.5% accuracy in Track 2)

Generate 800 privilege escalation samples:
1. SUID binary exploitation (100 samples)
2. Kernel privilege escalation (100 samples)
3. Container escape techniques (100 samples)
4. Windows UAC bypass (100 samples)
5. Linux capability abuse (100 samples)
6. Sudo misconfigurations (100 samples)
7. setuid vulnerabilities (100 samples)
8. Process injection for privilege gain (100 samples)

### Phase 2: High-Priority Categories (Week 1, Days 3-5)
- Buffer Overflow: 600 samples
- Path Traversal: 500 samples
- Malware: 700 samples

### Phase 3: Medium-Priority Categories (Week 2)
- SQL Injection: 600 samples
- XSS: 600 samples
- Command Injection: 500 samples
- Phishing: 500 samples
- DoS: 400 samples

### Phase 4: Low-Priority & Benign (Week 3)
- MITM: 300 samples
- Benign samples: 5,500 samples (match attack total)

### Quality Control
- Manual review: 10% of samples per category
- Automated validation: 100% of samples
- Deduplication: Run across all samples
- Labeling review: Reduce unknown to <10%

### Execution Commands
```bash
# On BETA system
ssh beta.local
cd /Volumes/DATA/GLADIATOR

# Generate samples (to be implemented)
# docker exec red_combat python3 /gladiator/scripts/generate_expansion_dataset.py
```

---

**Status**: READY TO LAUNCH (Week 1, Day 1)
