# GLADIATOR WEEK 1 EXECUTION PLAN
## Data Preparation & Network Upgrade

**Date**: October 23-29, 2025 (7 days)  
**Status**: ✅ **APPROVED TO START** (Week 0 GO decision)  
**Phase**: Week 1 of 8  
**Prerequisites**: ✅ Week 0 Reality Check v2.0 PASSED

---

## WEEK 1 OVERVIEW

**Primary Objectives**:
1. Install 10GbE network between ALPHA and BETA
2. Launch dataset expansion (Track 3) on BETA in parallel
3. Prepare infrastructure for Week 2-3 Blue Team training
4. Validate network performance and data transfer capabilities

**Success Criteria**:
- 10GbE network operational with ≥500 MB/s throughput
- Dataset expansion launched and progressing
- Infrastructure ready for 10K+ sample training
- Week 1 tasks completed on schedule

**Timeline**: 7 days (October 23-29, 2025)

---

## TASK BREAKDOWN

### DAY 1: Wednesday, October 23

**TASK 14: 10GbE Network Installation** 🔴 CRITICAL
```
Duration: 4-6 hours
System: ALPHA + BETA
Owner: Arthur

Description:
Install and configure 10GbE network connection between ALPHA and BETA
Mac Studio systems for high-speed data transfer.

Hardware Requirements:
├─ 10GbE Thunderbolt adapters (2×) or built-in 10GbE
├─ Cat 6a or Cat 7 Ethernet cable
├─ 10GbE network switch (if not direct connection)
└─ Thunderbolt 4 cables (if using adapters)

Installation Steps:
1. Connect 10GbE adapters to both systems
2. Configure network interfaces
3. Set static IP addresses (10.0.10.1 for ALPHA, 10.0.10.2 for BETA)
4. Test connectivity (ping, iperf3)
5. Measure throughput

Success Criteria:
├─ Network connectivity: PASS (ping successful)
├─ Throughput: ≥500 MB/s (measured with iperf3)
├─ Latency: <1ms
└─ Stability: No packet loss over 10-minute test

Verification:
# On ALPHA
sudo ifconfig en[X] 10.0.10.1 netmask 255.255.255.0
ping 10.0.10.2

# Throughput test (run iperf3 server on BETA)
iperf3 -c 10.0.10.2 -t 60

Evidence Required:
├─ iperf3 output showing ≥500 MB/s
├─ Network configuration screenshots
└─ Stability test results (0% packet loss)
```

**TASK 15: Launch Dataset Expansion (Track 3)** 🔴 CRITICAL
```
Duration: 2-4 hours (setup), then 2-3 weeks (generation)
System: BETA
Owner: Claude / Arthur

Description:
Launch parallel dataset expansion process on BETA to generate 11,000
high-quality samples (5,500 attacks + 5,500 benign) while Week 1-2
infrastructure work proceeds.

Prerequisites:
├─ BETA system accessible
├─ red_combat container running
├─ LM Studio operational (http://localhost:1234)
├─ Expansion plan ready (datasets/expansion_plan_track3.json)
└─ Storage available (≥50 GB free on /Volumes/DATA)

Phase 1 Setup:
1. Verify BETA system status
2. Check LM Studio model availability
3. Create generation scripts
4. Set up automated monitoring
5. Launch first batch (privilege escalation - 800 samples)

Success Criteria (Setup):
├─ Generation scripts created and tested
├─ First batch launched (privilege escalation)
├─ Monitoring system operational
└─ Progress tracking established

Verification:
ssh beta.local "docker ps | grep red_combat"
ssh beta.local "curl http://localhost:1234/v1/models"
ssh beta.local "ls -lh /Volumes/DATA/GLADIATOR/datasets/expansion/"

Evidence Required:
├─ First batch initiated (log file)
├─ Sample quality verified (manual review of first 10)
└─ Timeline established (samples per day estimate)
```

### DAY 2: Thursday, October 24

**TASK 16: Network Performance Validation** ⏳ HIGH
```
Duration: 2-3 hours
System: ALPHA + BETA
Owner: Arthur

Description:
Validate 10GbE network performance with actual data transfer scenarios
matching Week 2-3 Blue Team training requirements.

Test Scenarios:
1. Large file transfer (10 GB test file)
2. Multiple concurrent transfers
3. Sustained throughput test (1 hour)
4. Network stability under load

Success Criteria:
├─ Single file transfer: ≥500 MB/s
├─ Concurrent transfers: ≥400 MB/s (2 streams)
├─ Sustained performance: ≥450 MB/s over 1 hour
├─ Packet loss: <0.01%
└─ Latency: <1ms

Verification:
# Create 10GB test file
dd if=/dev/urandom of=/tmp/test_10gb.dat bs=1m count=10240

# Transfer test
time rsync -avh --progress /tmp/test_10gb.dat beta.local:/tmp/

Evidence Required:
├─ Transfer speed measurements
├─ Throughput graphs (if available)
└─ Stability test logs
```

**TASK 17: Monitor Dataset Expansion Progress** ⏳ ONGOING
```
Duration: 2-3 weeks (check daily)
System: BETA
Owner: Claude / Arthur

Description:
Monitor Track 3 dataset expansion progress, quality, and timeline.

Daily Checks:
├─ Samples generated count
├─ Quality spot-check (10 random samples)
├─ Category distribution
├─ Error rate
└─ Timeline projection

Progress Targets:
├─ Day 2: 200-400 samples (privilege escalation)
├─ Day 4: 600-800 samples (privilege escalation complete)
├─ Week 1 End: 1,500-2,000 samples (privilege + buffer overflow)
├─ Week 2 End: 5,000-7,000 samples
└─ Week 3 End: 11,000+ samples COMPLETE

Success Criteria:
├─ Daily progress ≥200 samples
├─ Quality rate ≥90% (manual review)
├─ Category diversity maintained
└─ On track for 3-week completion
```

### DAY 3-4: Friday-Saturday, October 25-26

**TASK 18: Prepare Blue Team Training Infrastructure** ⏳ HIGH
```
Duration: 8-12 hours
System: ALPHA
Owner: Claude / Arthur

Description:
Prepare ALPHA system for large-scale Blue Team training (Week 2-3).

Infrastructure Preparation:
1. Storage allocation (≥100 GB for datasets)
2. Training directory structure
3. Checkpoint storage strategy (RAID or redundant)
4. Monitoring dashboard setup
5. Resource allocation planning

Directory Structure:
/Users/arthurdell/GLADIATOR/
├─ datasets/
│   ├─ blue_team_training/
│   │   ├─ train.jsonl (80% of 10K = 8,000 samples)
│   │   ├─ valid.jsonl (20% of 10K = 2,000 samples)
│   │   └─ test.jsonl (separate test set)
│   └─ metadata/
├─ checkpoints/
│   └─ blue_team_8b/
│       ├─ iteration_checkpoints/
│       └─ final/
└─ logs/
    └─ blue_team_training/

Success Criteria:
├─ Storage allocated: ≥100 GB
├─ Directory structure created
├─ Monitoring system operational
├─ Resource plan documented
└─ Ready for 10K sample training

Verification:
df -h /Users/arthurdell/GLADIATOR
ls -la /Users/arthurdell/GLADIATOR/datasets/blue_team_training/

Evidence Required:
├─ Directory structure screenshot
├─ Storage allocation proof
└─ Monitoring dashboard operational
```

**TASK 19: Quality Review - First Dataset Expansion Batch** ⏳ HIGH
```
Duration: 3-4 hours
System: BETA → ALPHA
Owner: Arthur / Claude

Description:
Review first batch of expanded dataset (privilege escalation ~800 samples)
for quality, accuracy, and formatting.

Review Process:
1. Transfer first batch from BETA to ALPHA
2. Manual review of 80 samples (10%)
3. Automated validation (format, length, content)
4. Label accuracy check
5. Approve or request corrections

Quality Criteria:
├─ Label accuracy: ≥95% (manual review)
├─ Format valid: 100% (automated check)
├─ Content quality: ≥90% (coherent, realistic)
├─ Diversity: All 8 privilege escalation techniques represented
└─ No duplicates: <1% similarity to existing samples

Success Criteria:
├─ 80 samples manually reviewed
├─ Quality metrics meet thresholds
├─ Batch approved for inclusion
└─ Corrections identified (if needed)

Evidence Required:
├─ Review checklist (80 samples)
├─ Quality metrics report
└─ Approval decision documented
```

### DAY 5-6: Sunday-Monday, October 27-28

**TASK 20: Data Transfer Protocol Setup** ⏳ MEDIUM
```
Duration: 4-6 hours
System: ALPHA + BETA
Owner: Claude

Description:
Create automated data transfer protocol for moving expanded dataset
from BETA to ALPHA when ready.

Components:
1. Automated sync script (rsync over 10GbE)
2. Checksum verification
3. Progress monitoring
4. Error handling and retry logic
5. Transfer completion notification

Script Features:
├─ Incremental sync (only new files)
├─ MD5 checksum verification
├─ Bandwidth limiting (if needed)
├─ Logging and monitoring
└─ Automatic retry on failure

Success Criteria:
├─ Script created and tested
├─ Test transfer ≥500 MB/s
├─ Checksum verification works
├─ Error handling tested
└─ Ready for production use

Verification:
# Test with sample dataset
./scripts/sync_beta_to_alpha.sh --test

Evidence Required:
├─ Script file (sync_beta_to_alpha.sh)
├─ Test transfer log
└─ Checksum verification proof
```

### DAY 7: Tuesday, October 29

**TASK 21: Week 1 Completion Review** 🔴 CRITICAL
```
Duration: 2-3 hours
System: ALPHA
Owner: Claude / Arthur

Description:
Comprehensive review of Week 1 accomplishments and readiness for Week 2-3.

Review Checklist:
├─ 10GbE network: Operational at ≥500 MB/s
├─ Dataset expansion: On track (≥2,000 samples by Week 1 end)
├─ Quality review: First batch approved
├─ Infrastructure: Ready for Blue Team training
├─ Data transfer: Protocol tested and operational
└─ Timeline: On track for Week 2-3 start

Deliverables:
├─ Week 1 completion report
├─ Network performance report
├─ Dataset expansion progress report
├─ Week 2-3 readiness checklist
└─ GO/NO-GO decision for Week 2-3

Success Criteria:
├─ All Week 1 tasks complete
├─ No critical blockers
├─ Infrastructure validated
└─ Ready to proceed

Decision Gate:
IF all criteria met: GO to Week 2-3 (Blue Team Training)
IF blockers exist: Address before proceeding
```

---

## PARALLEL EXECUTION: DATASET EXPANSION (TRACK 3)

**Timeline**: 2-3 weeks (Oct 23 - Nov 13)  
**System**: BETA  
**Owner**: Claude / Arthur (rotating)

### Week 1 Target (Oct 23-29): 2,000 samples
```
Priority Batches:
├─ Privilege Escalation: 800 samples (Day 1-4)
├─ Buffer Overflow: 600 samples (Day 4-6)
└─ Path Traversal: 500 samples (Day 6-7)

Daily Target: ~285 samples/day
Quality Gate: Manual review 10% per batch
```

### Week 2 Target (Oct 30 - Nov 5): 4,000 samples (cumulative 6,000)
```
Medium Priority Batches:
├─ SQL Injection: 600 samples
├─ XSS: 600 samples
├─ Command Injection: 500 samples
├─ Phishing: 500 samples
├─ DoS: 400 samples
└─ Malware: 400 samples

Daily Target: ~570 samples/day
Quality Gate: Automated validation 100%, manual 5%
```

### Week 3 Target (Nov 6-13): 5,000 samples (cumulative 11,000)
```
Final Batches:
├─ MITM: 300 samples
├─ Malware (continued): 300 samples
├─ Benign samples: 4,400 samples
└─ Additional attacks: 1,000 samples (to reach 5,500)

Daily Target: ~715 samples/day
Quality Gate: Final review 100 random samples
Format Conversion: All to chat template
```

---

## RESOURCE REQUIREMENTS

### Network Hardware
```
Equipment:
├─ 10GbE Thunderbolt adapter × 2: $200-300 each
├─ Cat 6a cable (appropriate length): $20-50
└─ Optional: 10GbE switch: $500-1000 (if not direct)

Total Cost: ~$500-1,500
ROI: 5-10× faster data transfer, critical for timeline
```

### Storage
```
ALPHA:
├─ Dataset storage: ~50 GB (11K samples)
├─ Checkpoint storage: ~500 GB (training checkpoints)
├─ Log storage: ~10 GB
└─ Total needed: ~560 GB (available: 14+ TB ✅)

BETA:
├─ Generation workspace: ~100 GB
├─ Raw patterns: ~50 GB
└─ Total needed: ~150 GB (available: 16 TB ✅)
```

### Compute (Dataset Generation on BETA)
```
LM Studio:
├─ Model: Foundation-Sec-8B or similar
├─ Throughput: ~40 tokens/second
├─ Samples per hour: ~15-20 (depending on complexity)
└─ Daily capacity: 300-400 samples (with automation)

Resource Monitoring:
├─ RAM usage: ~50-100 GB (within 512 GB capacity)
├─ GPU utilization: ~60-80% (acceptable)
└─ Storage writes: ~2-5 GB/day
```

---

## SUCCESS METRICS

### Network Performance
```
Metric                    | Target    | Measurement Method
--------------------------|-----------|-------------------
Throughput (single)       | ≥500 MB/s | iperf3
Throughput (concurrent)   | ≥400 MB/s | parallel rsync
Latency                   | <1 ms     | ping statistics
Packet loss               | <0.01%    | long-duration ping
Stability                 | 24h uptime| continuous monitor
```

### Dataset Expansion (Week 1 Portion)
```
Metric                    | Target       | Measurement Method
--------------------------|--------------|-------------------
Samples generated         | ≥2,000       | file count
Quality rate              | ≥90%         | manual review
Category distribution     | Balanced     | automated analysis
Label accuracy            | ≥95%         | manual verification
Duplicate rate            | <1%          | similarity check
```

### Infrastructure Readiness
```
Metric                    | Status   | Verification Method
--------------------------|----------|--------------------
Storage allocated         | ≥100 GB  | df -h
Network operational       | Yes      | iperf3 + ping
Transfer protocol ready   | Yes      | test transfer
Monitoring operational    | Yes      | dashboard check
Ready for Week 2-3        | Yes      | checklist review
```

---

## RISK MITIGATION

### Risk 1: 10GbE Installation Issues
**Probability**: Medium  
**Impact**: High (delays Week 2-3)

Mitigation:
├─ Backup plan: Continue with 1GbE (slower but functional)
├─ Alternative: USB 3.2 Gen 2×2 (20 Gbps) for data transfer
├─ Contingency: Allow 1-2 extra days for troubleshooting
└─ Escalation: Engage network specialist if needed

### Risk 2: Dataset Expansion Behind Schedule
**Probability**: Medium  
**Impact**: Medium (can adjust Week 2-3 start)

Mitigation:
├─ Daily monitoring and adjustment
├─ Minimum viable: 5,000 samples (vs 11,000 target)
├─ Automation: Increase batch size if needed
├─ Parallel generation: Use multiple LLM instances
└─ Timeline flex: Week 2-3 can start with partial dataset

### Risk 3: Quality Issues in Generated Samples
**Probability**: Low  
**Impact**: High (bad training data = bad model)

Mitigation:
├─ Manual review 10% of samples per batch
├─ Automated validation 100% of samples
├─ Reject low-quality samples immediately
├─ Regenerate if batch quality <90%
└─ Expert review for ambiguous samples

---

## MONITORING & REPORTING

### Daily Status Updates
```
Format:
================================================================================
WEEK 1 DAY [X] STATUS - [DATE]
================================================================================

Network Status:
├─ 10GbE Installation: [COMPLETE / IN PROGRESS / NOT STARTED]
├─ Throughput: [XXX MB/s] (Target: ≥500 MB/s)
└─ Status: [OPERATIONAL / ISSUES / NOT READY]

Dataset Expansion (Track 3):
├─ Total Samples: [X,XXX] / 11,000
├─ Today Generated: [XXX] samples
├─ Quality Rate: [XX]% (Target: ≥90%)
├─ Current Batch: [Category name]
└─ Status: [ON TRACK / BEHIND / AHEAD]

Week 1 Progress:
├─ Tasks Complete: [X] / 8
├─ Days Elapsed: [X] / 7
├─ Timeline: [ON TRACK / AT RISK / DELAYED]
└─ Blockers: [NONE / list if any]

Next 24 Hours:
[Planned tasks]

================================================================================
```

### Weekly Summary (End of Week 1)
```
Required content:
├─ All tasks completed (Y/N with evidence)
├─ Network performance validated
├─ Dataset expansion progress
├─ Infrastructure readiness assessment
├─ Week 2-3 GO/NO-GO decision
└─ Evidence files and measurements
```

---

## WEEK 1 DELIVERABLES

### Infrastructure
1. ✅ 10GbE network operational (≥500 MB/s verified)
2. ✅ Data transfer protocol tested and documented
3. ✅ Storage allocated and organized
4. ✅ Monitoring system operational

### Data
1. ✅ Dataset expansion launched (Track 3)
2. ✅ First 2,000 samples generated (privilege escalation + buffer overflow)
3. ✅ Quality review completed on first batch
4. ✅ On track for 11,000 total by end of Week 3

### Documentation
1. ✅ Week 1 completion report
2. ✅ Network performance report
3. ✅ Dataset expansion progress report
4. ✅ Week 2-3 readiness checklist

---

## TRANSITION TO WEEK 2-3

### Prerequisites for Week 2-3 Start
```
MANDATORY:
├─ 10GbE network operational
├─ Dataset expansion ≥5,000 samples (minimum viable)
├─ Infrastructure ready (storage, monitoring)
└─ Week 1 completion approved

OPTIMAL:
├─ Dataset expansion ≥10,000 samples (full target)
├─ All quality reviews complete
├─ Network performance validated
└─ No outstanding issues
```

### Week 2-3 Preview
```
Task: Blue Team Training (Foundation-Sec-8B full-scale fine-tuning)
Duration: 14 days
Dataset: 8,000 train + 2,000 validation (from expanded 10K)
Target: ≥98% test accuracy
Deliverable: GLADIATOR-SEC-8B-EXPERT v1.0
```

---

## APPENDIX: COMMANDS REFERENCE

### Network Setup (10GbE)
```bash
# ALPHA configuration
sudo ifconfig en[X] 10.0.10.1 netmask 255.255.255.0 up

# BETA configuration  
sudo ifconfig en[X] 10.0.10.2 netmask 255.255.255.0 up

# Test connectivity
ping 10.0.10.2  # from ALPHA
ping 10.0.10.1  # from BETA

# Throughput test (server on BETA, client on ALPHA)
# BETA: iperf3 -s
# ALPHA: iperf3 -c 10.0.10.2 -t 60 -P 4
```

### Dataset Monitoring
```bash
# Check generation progress on BETA
ssh beta.local "ls -1 /Volumes/DATA/GLADIATOR/datasets/expansion/*.jsonl | wc -l"

# Count samples
ssh beta.local "wc -l /Volumes/DATA/GLADIATOR/datasets/expansion/*.jsonl"

# Quality check
ssh beta.local "head -10 /Volumes/DATA/GLADIATOR/datasets/expansion/privilege_escalation_batch1.jsonl"
```

### Infrastructure Validation
```bash
# Storage check
df -h /Users/arthurdell/GLADIATOR

# GPU availability
python3 -c "import mlx.core as mx; print(f'GPU: {mx.metal.is_available()}, Cores: 80')"

# Database status
PGPASSWORD='Power$$336633$$' psql -U postgres -d aya_rag -c "SELECT current_phase, current_week FROM gladiator_project_state WHERE is_current = true;"
```

---

**Week 1 Plan Status**: ✅ READY TO EXECUTE  
**Prerequisites**: ✅ Week 0 GO decision achieved  
**Timeline**: 7 days (October 23-29, 2025)  
**Next Review**: End of Day 1 (network installation)

---

**END OF WEEK 1 EXECUTION PLAN**

