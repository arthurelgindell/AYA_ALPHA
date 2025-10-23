#!/bin/bash
#
# GLADIATOR Week 2-3 Automated Pipeline
# Execute: Dataset prep → Training → Validation → GO/NO-GO
# Runs immediately once attack expansion completes
#

set -e

echo "================================================================================"
echo "GLADIATOR WEEK 2-3 AUTOMATED PIPELINE"
echo "================================================================================"
echo "Started: $(date)"
echo ""

# ============================================================================
# PHASE 1: DATASET PREPARATION
# ============================================================================

echo "PHASE 1: Dataset Preparation"
echo "============================================================================"
echo ""

# Wait for attack generation to complete
echo "Checking attack expansion status..."
while true; do
    if ssh beta.local "test -f /Volumes/DATA/GLADIATOR/datasets/expansion/attack_expansion_800.jsonl"; then
        ATTACK_EXP_COUNT=$(ssh beta.local "wc -l < /Volumes/DATA/GLADIATOR/datasets/expansion/attack_expansion_800.jsonl")
        if [ "$ATTACK_EXP_COUNT" -ge 800 ]; then
            echo "✅ Attack expansion complete: $ATTACK_EXP_COUNT samples"
            break
        else
            echo "  In progress: $ATTACK_EXP_COUNT / 800 samples... (waiting 5 min)"
            sleep 300
        fi
    else
        echo "  Waiting for attack expansion to start... (checking in 2 min)"
        sleep 120
    fi
done

echo ""

# Transfer attack samples from BETA
echo "Transferring attack expansion from BETA..."
scp beta.local:/Volumes/DATA/GLADIATOR/datasets/expansion/attack_expansion_800.jsonl \
    datasets/expansion/

echo "✅ Transfer complete"
echo ""

# Run dataset preparation
echo "Combining all samples (5,000 total)..."
./datasets/prepare_5k_dataset.sh

echo ""

# Prepare train/valid split
echo "Creating train/valid split..."
python3 training/prepare_blue_team_dataset.py \
    --attack-sources datasets/blue_team_5k/attacks_combined_2500.jsonl \
    --benign-sources datasets/blue_team_5k/benign_2500.jsonl \
    --output-dir datasets/blue_team_training \
    --total-samples 5000 \
    --train-split 0.8

echo "✅ Dataset preparation complete"
echo "   Training: $(wc -l < datasets/blue_team_training/train.jsonl) samples"
echo "   Validation: $(wc -l < datasets/blue_team_training/valid.jsonl) samples"
echo ""

# ============================================================================
# PHASE 2: TRAINING
# ============================================================================

echo ""
echo "PHASE 2: Blue Team Training"
echo "============================================================================"
echo ""

read -p "Proceed with training? (yes/no): " PROCEED
if [ "$PROCEED" != "yes" ]; then
    echo "Pipeline paused. Resumelater with: ./launch_week2_3_pipeline.sh"
    exit 0
fi

./training/launch_blue_team_training.sh

echo "✅ Training complete"
echo ""

# ============================================================================
# PHASE 3: VALIDATION
# ============================================================================

echo ""
echo "PHASE 3: Validation"
echo "============================================================================"
echo ""

python3 training/validate_blue_team_model.py

echo "✅ Validation complete"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "================================================================================"
echo "WEEK 2-3 PIPELINE COMPLETE"
echo "================================================================================"
echo "Completed: $(date)"
echo ""
echo "Results:"
echo "  - Dataset: 5,000 samples (2,500 attack + 2,500 benign)"
echo "  - Training: 500 iterations complete"
echo "  - Validation: Results in results/blue_team_validation_results.json"
echo ""
echo "Check validation results for GO/NO-GO decision:"
echo "  cat results/blue_team_validation_results.json | jq '.decision'"
echo ""
echo "================================================================================"

