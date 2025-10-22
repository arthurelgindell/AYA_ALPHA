#!/bin/bash
#
# GLADIATOR Binary Classification Training
# Launch fine-tuning for attack vs benign detection
#

set -e

echo "======================================================================="
echo "GLADIATOR Binary Classification Training"
echo "======================================================================="
echo ""
echo "Configuration:"
echo "  Model: Foundation-Sec-8B-Instruct-int8"
echo "  Training samples: 1,800 (900 attack + 900 benign)"
echo "  Validation samples: 200 (100 attack + 100 benign)"
echo "  Iterations: 100"
echo "  Batch size: 4"
echo "  Learning rate: 1e-4"
echo "  LoRA rank: 16"
echo ""

# Paths
MODEL_PATH="/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
DATA_DIR="/Users/arthurdell/GLADIATOR/training/binary_classification_data"
OUTPUT_DIR="/Users/arthurdell/GLADIATOR/checkpoints/binary_classification"
LOG_DIR="/Users/arthurdell/GLADIATOR/logs/binary_classification"

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
cp /Users/arthurdell/GLADIATOR/training/reality_check_data/binary_train_1800.jsonl "$DATA_DIR/train.jsonl"
cp /Users/arthurdell/GLADIATOR/training/reality_check_data/binary_val_200.jsonl "$DATA_DIR/valid.jsonl"
cp /Users/arthurdell/GLADIATOR/training/reality_check_data/binary_val_200.jsonl "$DATA_DIR/test.jsonl"

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
    --val-batches 25 \
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

