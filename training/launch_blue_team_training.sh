#!/bin/bash
#
# GLADIATOR Blue Team Training Launcher
# Train Foundation-Sec-8B on 11,000 balanced samples
#

set -e

echo "================================================================================"
echo "GLADIATOR Blue Team Training - Production Run"
echo "================================================================================"
echo "Started: $(date)"
echo ""

# Configuration
MODEL_PATH="/Users/arthurdell/AYA/projects/GLADIATOR/blue_team/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
DATA_DIR="/Users/arthurdell/AYA/projects/GLADIATOR/blue_team/datasets/blue_team_training"
OUTPUT_DIR="/Users/arthurdell/AYA/projects/GLADIATOR/blue_team/checkpoints/blue_team_8b"
LOG_DIR="/Users/arthurdell/AYA/projects/GLADIATOR/blue_team/logs/blue_team_training"

# Training parameters
ITERATIONS=500
BATCH_SIZE=4
LEARNING_RATE=1e-4
LORA_LAYERS=16
LORA_ALPHA=32
SAVE_EVERY=50
VAL_EVERY=50

echo "Configuration:"
echo "  Model: Foundation-Sec-8B-Instruct-int8"
echo "  Training samples: $(wc -l < $DATA_DIR/train.jsonl 2>/dev/null || echo 'N/A')"
echo "  Validation samples: $(wc -l < $DATA_DIR/valid.jsonl 2>/dev/null || echo 'N/A')"
echo "  Iterations: $ITERATIONS"
echo "  Batch size: $BATCH_SIZE"
echo "  Learning rate: $LEARNING_RATE"
echo "  LoRA rank: $LORA_LAYERS"
echo "  LoRA alpha: $LORA_ALPHA"
echo ""

# Create directories
mkdir -p "$OUTPUT_DIR/iteration_checkpoints"
mkdir -p "$OUTPUT_DIR/final"
mkdir -p "$LOG_DIR"

# Verify prerequisites
echo "Verifying prerequisites..."

if [ ! -d "$MODEL_PATH" ]; then
    echo "❌ ERROR: Model not found at $MODEL_PATH"
    exit 1
fi
echo "  ✅ Model found"

if [ ! -f "$DATA_DIR/train.jsonl" ]; then
    echo "❌ ERROR: Training data not found at $DATA_DIR/train.jsonl"
    exit 1
fi
echo "  ✅ Training data found"

if [ ! -f "$DATA_DIR/valid.jsonl" ]; then
    echo "❌ ERROR: Validation data not found at $DATA_DIR/valid.jsonl"
    exit 1
fi
echo "  ✅ Validation data found"

# Check MLX GPU
echo "  Checking MLX GPU..."
python3 -c "import mlx.core as mx; print(f'  ✅ MLX GPU: {mx.metal.is_available()}, Device: {mx.default_device()}')" 2>/dev/null || {
    echo "  ⚠️  MLX GPU check failed (will try anyway)"
}

echo ""

# Display sample counts
TRAIN_COUNT=$(wc -l < "$DATA_DIR/train.jsonl")
VALID_COUNT=$(wc -l < "$DATA_DIR/valid.jsonl")

echo "Dataset Summary:"
echo "  Training samples: $TRAIN_COUNT"
echo "  Validation samples: $VALID_COUNT"
echo "  Total: $((TRAIN_COUNT + VALID_COUNT))"
echo ""

# Estimate training time
# Assume ~30-60 seconds per iteration
EST_MIN=$((ITERATIONS * 30 / 60))
EST_MAX=$((ITERATIONS * 60 / 60))
echo "Estimated training time: $EST_MIN - $EST_MAX minutes (${EST_MIN}m - ${EST_MAX}m)"
echo ""

# Confirmation prompt
read -p "Proceed with training? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Training cancelled by user"
    exit 0
fi

echo ""
echo "================================================================================"
echo "Starting Training"
echo "================================================================================"
echo ""

# Launch MLX-LM LoRA training
python3 -m mlx_lm.lora \
    --model "$MODEL_PATH" \
    --data "$DATA_DIR" \
    --train \
    --iters $ITERATIONS \
    --batch-size $BATCH_SIZE \
    --learning-rate $LEARNING_RATE \
    --lora-layers $LORA_LAYERS \
    --lora-alpha $LORA_ALPHA \
    --save-every $SAVE_EVERY \
    --adapter-path "$OUTPUT_DIR" \
    --test \
    2>&1 | tee "$LOG_DIR/training.log"

TRAIN_EXIT_CODE=$?

echo ""
echo "================================================================================"

if [ $TRAIN_EXIT_CODE -eq 0 ]; then
    echo "✅ Training completed successfully"
    echo "================================================================================"
    
    # Save final checkpoint info
    echo "Saving checkpoint metadata..."
    
    cat > "$OUTPUT_DIR/final/training_info.json" << EOF
{
  "completed": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "model": "Foundation-Sec-8B-Instruct-int8",
  "iterations": $ITERATIONS,
  "batch_size": $BATCH_SIZE,
  "learning_rate": $LEARNING_RATE,
  "lora_rank": $LORA_LAYERS,
  "lora_alpha": $LORA_ALPHA,
  "train_samples": $TRAIN_COUNT,
  "valid_samples": $VALID_COUNT,
  "checkpoint_path": "$OUTPUT_DIR",
  "log_path": "$LOG_DIR/training.log"
}
EOF
    
    echo "  ✅ Training metadata saved"
    echo ""
    
    # Display final checkpoints
    echo "Checkpoints saved:"
    ls -lh "$OUTPUT_DIR"/*.safetensors 2>/dev/null || echo "  (No .safetensors files found)"
    echo ""
    
    # Parse final loss from log
    FINAL_LOSS=$(tail -50 "$LOG_DIR/training.log" | grep -i "loss" | tail -1 | grep -oE "[0-9]+\.[0-9]+" | head -1)
    if [ -n "$FINAL_LOSS" ]; then
        echo "Final training loss: $FINAL_LOSS"
        
        if (( $(echo "$FINAL_LOSS < 0.5" | bc -l) )); then
            echo "  ✅ Loss converged (< 0.5)"
        elif (( $(echo "$FINAL_LOSS < 1.0" | bc -l) )); then
            echo "  ⚠️  Loss acceptable but could be better (< 1.0)"
        else
            echo "  ⚠️  Loss high (≥ 1.0) - may need more iterations"
        fi
    fi
    
    echo ""
    echo "Next steps:"
    echo "  1. Review training log: $LOG_DIR/training.log"
    echo "  2. Run validation: ./training/validate_blue_team_model.py"
    echo "  3. Check accuracy against ≥95% target"
    echo ""
    
else
    echo "❌ Training failed with exit code $TRAIN_EXIT_CODE"
    echo "================================================================================"
    echo "Check log for errors: $LOG_DIR/training.log"
    echo ""
    exit $TRAIN_EXIT_CODE
fi

echo "================================================================================"
echo "Training run complete: $(date)"
echo "================================================================================"

