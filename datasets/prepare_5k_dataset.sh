#!/bin/bash
#
# Prepare 5K dataset for Blue Team training
# Combines privilege escalation (800) + reality check (900) + expansion (800) + benign (2,500)
#

set -e

echo "========================================================================"
echo "GLADIATOR 5K Dataset Preparation"
echo "========================================================================"
echo "Started: $(date)"
echo ""

OUTPUT_DIR="/Users/arthurdell/GLADIATOR/datasets/blue_team_5k"
mkdir -p "$OUTPUT_DIR"

echo "Combining attack samples..."

# Combine attack samples
cat /Users/arthurdell/GLADIATOR/datasets/expansion/privilege_escalation_batch1.jsonl \
    /Users/arthurdell/GLADIATOR/datasets/reality_check_train_900.jsonl \
    /Users/arthurdell/GLADIATOR/datasets/expansion/attack_expansion_800.jsonl \
    > "$OUTPUT_DIR/attacks_combined_2500.jsonl"

ATTACK_COUNT=$(wc -l < "$OUTPUT_DIR/attacks_combined_2500.jsonl")
echo "  ✅ Attack samples: $ATTACK_COUNT"

echo "Copying benign samples..."
cp /Users/arthurdell/GLADIATOR/datasets/expansion/benign_batch_2500.jsonl \
   "$OUTPUT_DIR/benign_2500.jsonl"

BENIGN_COUNT=$(wc -l < "$OUTPUT_DIR/benign_2500.jsonl")
echo "  ✅ Benign samples: $BENIGN_COUNT"

echo ""
echo "Total samples: $((ATTACK_COUNT + BENIGN_COUNT))"
echo ""

if [ "$ATTACK_COUNT" -ne 2500 ] || [ "$BENIGN_COUNT" -ne 2500 ]; then
    echo "❌ ERROR: Sample counts don't match expected (2500 each)"
    echo "   Attack: $ATTACK_COUNT (expected 2500)"
    echo "   Benign: $BENIGN_COUNT (expected 2500)"
    exit 1
fi

echo "✅ Dataset preparation complete"
echo "   Attack: 2,500 samples"
echo "   Benign: 2,500 samples"
echo "   Total: 5,000 samples (perfectly balanced)"
echo ""
echo "Next: Run prepare_blue_team_dataset.py to create train/valid split"
echo "========================================================================"
