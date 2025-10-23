# WEEK 2-3 DATASET STRATEGY - OPTIMIZED

**Date**: October 23, 2025, 08:45 PST  
**Status**: Early start (7 days ahead of schedule)  
**Revised Timeline**: Oct 23 - Nov 5, 2025 (14 days)

---

## CURRENT DATASET INVENTORY

### Existing Samples (VERIFIED):

**Attack Samples** (1,664 total):
- ✅ Privilege escalation: 800 (NEW, high quality, 8 subcategories)
- ✅ Reality check attacks: 664 (from Week 0 multi-class training)
  - SQL injection: ~83
  - XSS: ~83
  - Phishing: ~83
  - Command injection: ~83
  - DoS: ~83
  - MITM: ~83
  - Buffer overflow: ~83
  - Unknown: ~83

**Benign Samples** (1,000 total):
- ✅ Binary classification benign: 1,000 (train 900 + val 100)

**TOTAL CURRENT**: 2,664 samples (attack: 1,664, benign: 1,000)

---

## TARGET vs REALITY ASSESSMENT

### Original Target:
- Total: 11,000 samples
- Attack: 5,500
- Benign: 5,500

### Realistic Assessment:

**Attack Samples**:
- Have: 1,664 (privilege esc 800 + reality check 664)
- Quality: HIGH (privilege esc), GOOD (reality check - 92.96% validated)
- Need: 3,836 more for 5,500 target

**Benign Samples**:
- Have: 1,000
- Quality: HIGH (98.83% binary accuracy)
- Need: 4,500 more for 5,500 target

**TOTAL NEED**: 8,336 additional samples

---

## REVISED STRATEGY - PRAGMATIC APPROACH

### Option A: Full 11K (Original Plan)
- Generate 8,336 additional samples
- Timeline: 2-3 weeks (overlaps Week 2-3)
- Risk: May delay training start
- Benefit: Maximum dataset size

### Option B: Optimized 5K (Recommended)
- Use existing 2,664 samples
- Generate 2,336 additional (balanced)
- Total: 5,000 samples (2,500 attack + 2,500 benign)
- Timeline: 1-2 days
- Benefit: Start training immediately with high-quality base

### Option C: Hybrid Approach (Best Balance)
- Phase 1: Use existing 2,664 + generate 1,336 = 4,000 samples
  - Attack: 2,000 (existing 1,664 + 336 new)
  - Benign: 2,000 (existing 1,000 + 1,000 new)
- Train initial model (iterations 1-250)
- Phase 2: Generate additional 3,000 while training
- Phase 3: Retrain or continue with expanded dataset

---

## RECOMMENDED: OPTION B (5K OPTIMIZED)

**Rationale**:
1. Existing data is HIGH QUALITY (98.83% binary, 92.96% multi-class)
2. Privilege escalation now has 800 samples (vs 8 original)
3. Can start training TODAY vs waiting 2-3 weeks
4. 5,000 samples sufficient for LoRA fine-tuning
5. Can expand later if needed

**Required Generation**:
- Attack samples: 836 (to reach 2,500 total)
  - Buffer overflow: 200
  - Additional attack types: 636
- Benign samples: 1,500 (to reach 2,500 total)

**Timeline**: 
- Generation: 6-8 hours (~40 samples/hour @ 3.3/min)
- Start training: Oct 23 evening or Oct 24 morning
- Training complete: Oct 24-25 (500 iterations in 4-8 hours)
- Validation: Oct 25-26
- GO/NO-GO: Oct 26 (vs Nov 11 original)

**Benefit**: Complete Week 2-3 in 4 days vs 14 days, 10 days ahead

---

## GENERATION PLAN - OPTION B

### Attack Samples (836 needed):

**Buffer Overflow** (200 samples):
- Format: Similar to privilege escalation
- Generate via LM Studio on BETA
- Time: ~1 hour

**Additional Mixed Attack Types** (636 samples):
- Expand existing reality check categories
- Use proven templates from Week 0
- Time: ~3-4 hours

### Benign Samples (1,500 needed):

**Expand Existing Categories**:
- Legitimate SQL: +300 (200 → 500)
- Normal HTTP: +300 (200 → 500)
- Valid commands: +300 (200 → 500)
- Normal web traffic: +300 (200 → 500)
- Misc benign: +300 (200 → 500)

**Method**: Extend benign_samples_generator.py
**Time**: ~2 hours (deterministic generation, no LM Studio)

**TOTAL TIME**: 6-8 hours for 2,336 additional samples

---

## EXECUTION PLAN - STARTING NOW

### Today (Oct 23, 08:45 - 20:00):

**08:45-10:00**: Generate benign samples (1,500)
- Extend benign_samples_generator.py to 2,500 total
- Run on ALPHA (no LM Studio needed)
- Output: benign_train_2500.jsonl

**10:00-14:00**: Generate buffer overflow samples (200)
- Create buffer_overflow_generator.py
- Run on BETA (LM Studio)
- Output: buffer_overflow_batch.jsonl

**14:00-18:00**: Generate additional attack samples (636)
- Extend reality check categories
- Mix of all attack types
- Output: attack_expansion_batch.jsonl

**18:00-20:00**: Combine and prepare dataset
- Total: 5,000 samples (2,500 attack + 2,500 benign)
- Run prepare_blue_team_dataset.py
- Output: train.jsonl (4,000) + valid.jsonl (1,000)

### Tomorrow (Oct 24):

**09:00-17:00**: Blue Team Training
- Launch MLX-LM LoRA training
- 500 iterations, ~4-8 hours
- Monitor and checkpoint

**17:00-20:00**: Validation
- Run full validation on 1,000 samples
- Calculate accuracy, precision, recall
- Prepare results

### Oct 25-26: GO/NO-GO Decision

**Oct 25**: Error analysis and decision prep
**Oct 26**: Final GO/NO-GO for Week 4 (Red Team)

---

## REVISED TIMELINE SUMMARY

| Phase | Original | Revised | Variance |
|-------|----------|---------|----------|
| Week 1 | Oct 23-29 | Oct 23 | -6 days |
| Week 2-3 | Oct 30 - Nov 12 | Oct 23 - Nov 5 | -7 days |
| Week 4 | Nov 13-19 | Nov 6-12 | -7 days |
| Completion | Dec 11 | Dec 4 | -7 days ahead |

**New Deadline**: Potential completion Dec 4 (vs Dec 11 original)
**Buffer**: 7 additional days for contingencies

---

**WEEK 2-3 EXECUTION: STARTING NOW**

First task: Generate 1,500 benign samples (deterministic, fast)

================================================================================
