#!/bin/bash
#
# GLADIATOR Multi-Class Attack Detection Training
# Launch fine-tuning for attack type classification
#

set -e

echo "======================================================================="
echo "GLADIATOR Multi-Class Attack Detection Training"
echo "======================================================================="
echo ""
echo "Configuration:"
echo "  Model: Foundation-Sec-8B-Instruct-int8 (fresh, not from binary)"
echo "  Training samples: 664 (attack samples only)"
echo "  Validation samples: 71 (attack samples only)"
echo "  Iterations: 100"
echo "  Batch size: 4"
echo "  Learning rate: 1e-4"
echo "  LoRA layers: 16"
echo ""

# Paths
MODEL_PATH="/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
DATA_DIR="/Users/arthurdell/GLADIATOR/training/multiclass_detection_data"
OUTPUT_DIR="/Users/arthurdell/GLADIATOR/checkpoints/multiclass_detection"
LOG_DIR="/Users/arthurdell/GLADIATOR/logs/multiclass_detection"

# Create directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"

# Verify model exists
echo "Verifying files..."
if [ ! -d "$MODEL_PATH" ]; then
    echo "❌ ERROR: Model not found at $MODEL_PATH"
    exit 1
fi

# Copy data files to expected location (MLX-LM expects train.jsonl, valid.jsonl, and test.jsonl)
echo "Preparing data directory..."
cp /Users/arthurdell/GLADIATOR/training/reality_check_data/multiclass_train_900.jsonl "$DATA_DIR/train.jsonl"
cp /Users/arthurdell/GLADIATOR/training/reality_check_data/multiclass_val_100.jsonl "$DATA_DIR/valid.jsonl"
cp /Users/arthurdell/GLADIATOR/training/reality_check_data/multiclass_val_100.jsonl "$DATA_DIR/test.jsonl"

if [ ! -f "$DATA_DIR/train.jsonl" ] || [ ! -f "$DATA_DIR/valid.jsonl" ] || [ ! -f "$DATA_DIR/test.jsonl" ]; then
    echo "❌ ERROR: Failed to prepare data files"
    exit 1
fi

echo "✅ All files verified"
echo "✅ Data directory: $DATA_DIR"
echo ""

# Launch training
echo "Starting training at $(date)"
echo ""

cd /Users/arthurdell/GLADIATOR

python3 -m mlx_lm.lora \
    --model "$MODEL_PATH" \
    --train \
    --data "$DATA_DIR" \
    --batch-size 4 \
    --num-layers 16 \
    --iters 100 \
    --steps-per-report 10 \
    --steps-per-eval 50 \
    --val-batches 17 \
    --learning-rate 1e-4 \
    --save-every 50 \
    --adapter-path "$OUTPUT_DIR" \
    --test \
    2>&1 | tee "$LOG_DIR/training.log"

echo ""
echo "======================================================================="
echo "Training complete at $(date)"
echo "======================================================================="
echo "Checkpoints: $OUTPUT_DIR"
echo "Logs: $LOG_DIR/training.log"
echo ""

