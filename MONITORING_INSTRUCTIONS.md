# GLADIATOR Monitoring Instructions

**Last Updated**: October 22, 2025, 22:35 PST  
**Status**: Dataset generation running, monitoring required

---

## CURRENT STATE

**Dataset Generation**:
- Process: RUNNING (PID 19367 on BETA)
- Started: Oct 22, 22:26 PST
- Target: 800 privilege escalation samples
- Rate: ~3.3 samples/minute
- Expected: Oct 23, 02:00-08:00 PST (3.5-10 hours)

**Outstanding Task**:
- Task 19: Quality review (pending 80+ samples)

---

## MONITORING COMMANDS

### Quick Status Check (Run Every 2-4 Hours)

```bash
cd /Users/arthurdell/GLADIATOR
./scripts/monitor_expansion.sh
```

This will show:
- Process status (running/stopped)
- Sample count (if any)
- Progress percentage
- ETA calculation
- Storage status

### Manual Checks

**Check process is running**:
```bash
ssh beta.local "ps aux | grep generate_privilege_escalation | grep -v grep"
```
Expected: PID 19367 or similar

**Check samples generated**:
```bash
ssh beta.local "ls -lh /Volumes/DATA/GLADIATOR/datasets/expansion/"
ssh beta.local "wc -l /Volumes/DATA/GLADIATOR/datasets/expansion/*.jsonl 2>/dev/null"
```
Expected: privilege_escalation_batch1.jsonl with increasing line count

**Check log for errors**:
```bash
ssh beta.local "tail -50 /Volumes/DATA/GLADIATOR/datasets/generation_batch1.log"
```
Expected: Progress messages, no errors

---

## WHEN TO RUN QUALITY REVIEW

**Trigger**: When 80+ samples are generated

**Check sample count**:
```bash
ssh beta.local "wc -l /Volumes/DATA/GLADIATOR/datasets/expansion/privilege_escalation_batch1.jsonl"
```

**If count ≥ 80**, run quality review:
```bash
cd /Users/arthurdell/GLADIATOR

# Copy samples to ALPHA for review
scp beta.local:/Volumes/DATA/GLADIATOR/datasets/expansion/privilege_escalation_batch1.jsonl datasets/expansion/

# Run quality check
python3 training/quality_check.py datasets/expansion/privilege_escalation_batch1.jsonl

# Review results
cat quality_check_report.json
```

**Quality Check Results**:
- PASS: Continue generation
- PASS WITH WARNINGS: Review warnings, decide if acceptable
- FAIL: Stop generation, fix issues, restart

---

## IF GENERATION FAILS

**Symptoms**:
- Process not running (ps aux shows nothing)
- No new samples for >1 hour
- Error messages in log

**Steps to diagnose**:

1. **Check log for errors**:
```bash
ssh beta.local "tail -100 /Volumes/DATA/GLADIATOR/datasets/generation_batch1.log"
```

2. **Check process exit code** (if stopped):
```bash
ssh beta.local "echo $?"
```

3. **Common issues**:
- LM Studio not responding: Restart LM Studio
- Out of memory: Check available RAM
- Network timeout: Check BETA connectivity
- Template error: Check log for KeyError or similar

**To restart generation**:
```bash
ssh beta.local "cd /Volumes/DATA/GLADIATOR/datasets && nohup python3 generate_privilege_escalation_batch.py > generation_batch1.log 2>&1 &"

# Verify it started
ssh beta.local "ps aux | grep generate_privilege_escalation | grep -v grep"
```

---

## WHEN GENERATION COMPLETES

**Check completion**:
```bash
ssh beta.local "wc -l /Volumes/DATA/GLADIATOR/datasets/expansion/privilege_escalation_batch1.jsonl"
```
Expected: 800 lines

**Verify all categories completed**:
```bash
ssh beta.local "tail -50 /Volumes/DATA/GLADIATOR/datasets/generation_batch1.log"
```
Expected: "✅ All categories complete" or similar

**Transfer to ALPHA**:
```bash
cd /Users/arthurdell/GLADIATOR
./scripts/sync_beta_to_alpha.sh
```

**Run final quality check**:
```bash
python3 training/quality_check.py datasets/expansion/privilege_escalation_batch1.jsonl
```

**If quality check passes**:
- Update Week 1 status
- Mark Task 19 complete
- Prepare for Week 1 completion review

---

## EXPECTED TIMELINE

| Time | Event | Action |
|------|-------|--------|
| Oct 22, 22:26 | Generation started | Monitor every 2-4 hours |
| Oct 23, 00:00 | ~100-200 samples | Check progress, verify no errors |
| Oct 23, 02:00 | ~300-400 samples (optimistic) | Run quality review if ≥80 |
| Oct 23, 04:00 | ~500-600 samples | Verify steady progress |
| Oct 23, 06:00 | ~700-800 samples | Check for completion |
| Oct 23, 08:00 | 800 samples (conservative) | Transfer and quality check |

**Actual completion may vary ±6 hours depending on LM Studio performance**

---

## MONITORING SCHEDULE

### Recommended Schedule

**Tonight (Oct 22)**:
- 23:00: Check progress (30 min after start)
- 00:00: Check progress (~60 min of generation)

**Tomorrow (Oct 23)**:
- 02:00: Check progress (~3.5 hours, optimistic completion)
- 04:00: Check progress (if not complete)
- 06:00: Check progress (if not complete)
- 08:00: Check progress (conservative completion)
- 10:00: Check progress (if still running)

**Run quality review as soon as 80+ samples available**

---

## CONTACT POINTS

**Logs**:
- Generation: `/Volumes/DATA/GLADIATOR/datasets/generation_batch1.log` (on BETA)
- Monitor: Check monitor_expansion.sh output

**Data**:
- Samples: `/Volumes/DATA/GLADIATOR/datasets/expansion/` (on BETA)
- Quality report: `quality_check_report.json` (on ALPHA after review)

**Documentation**:
- This file: `MONITORING_INSTRUCTIONS.md`
- Comprehensive status: `WEEK_1_COMPREHENSIVE_STATUS.md`
- Session summary: `SESSION_SUMMARY_2025-10-22.md`

---

## AUTOMATION (OPTIONAL)

**To automate monitoring** (check every 2 hours):
```bash
# Add to crontab
0 */2 * * * cd /Users/arthurdell/GLADIATOR && ./scripts/monitor_expansion.sh >> logs/monitor_auto.log 2>&1
```

**To get notifications** when complete:
```bash
# Create notification script
cat > /Users/arthurdell/GLADIATOR/scripts/notify_complete.sh << 'EOF'
#!/bin/bash
SAMPLES=$(ssh beta.local "wc -l /Volumes/DATA/GLADIATOR/datasets/expansion/*.jsonl 2>/dev/null | tail -1 | awk '{print \$1}'")
if [ "$SAMPLES" -ge 800 ]; then
    osascript -e 'display notification "Dataset generation complete: 800 samples" with title "GLADIATOR"'
fi
EOF
chmod +x /Users/arthurdell/GLADIATOR/scripts/notify_complete.sh

# Run every 30 minutes
*/30 * * * * /Users/arthurdell/GLADIATOR/scripts/notify_complete.sh
```

---

## SUMMARY

**Current Status**: Generation running (PID 19367)  
**Monitor**: Every 2-4 hours with `./scripts/monitor_expansion.sh`  
**Quality Review**: When 80+ samples available  
**Expected Complete**: Oct 23, 02:00-08:00 PST  

**Next Action**: Monitor in 2-4 hours

---

**Created**: October 22, 2025, 22:35 PST  
**Process**: PID 19367 on BETA  
**Monitor Command**: `cd /Users/arthurdell/GLADIATOR && ./scripts/monitor_expansion.sh`

