#!/bin/bash
#
# GLADIATOR Week 0 - Reality Check Training Launch
# Fine-tune Foundation-Sec-8B on 900 adversarial samples using MLX-LM LoRA
#

set -e

# Configuration
MODEL_PATH="/Users/arthurdell/GLADIATOR/models/DavidBianco/Foundation-Sec-8B-Instruct-int8"
DATA_DIR="/Users/arthurdell/GLADIATOR/training/reality_check_data"
ADAPTER_PATH="/Users/arthurdell/GLADIATOR/checkpoints/reality_check"
LOG_FILE="/Users/arthurdell/GLADIATOR/logs/reality_check/training.log"
PID_FILE="/Users/arthurdell/GLADIATOR/logs/reality_check/training.pid"

# Training hyperparameters
BATCH_SIZE=4              # Conservative for 64GB RAM
ITERS=100                 # 100 training iterations
LEARNING_RATE=1e-4        # Standard LoRA learning rate
STEPS_PER_REPORT=10       # Report every 10 steps
STEPS_PER_EVAL=50         # Validate every 50 steps
SAVE_EVERY=50             # Save checkpoint every 50 steps
NUM_LAYERS=16             # Number of layers to fine-tune
MAX_SEQ_LENGTH=2048       # Maximum sequence length
LORA_RANK=16              # LoRA rank (higher = more parameters)

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$ADAPTER_PATH"

# Log start time
echo "========================================" | tee -a "$LOG_FILE"
echo "GLADIATOR Reality Check Training" | tee -a "$LOG_FILE"
echo "Start Time: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Model: $MODEL_PATH" | tee -a "$LOG_FILE"
echo "Data: $DATA_DIR" | tee -a "$LOG_FILE"
echo "Output: $ADAPTER_PATH" | tee -a "$LOG_FILE"
echo "Batch Size: $BATCH_SIZE" | tee -a "$LOG_FILE"
echo "Iterations: $ITERS" | tee -a "$LOG_FILE"
echo "Learning Rate: $LEARNING_RATE" | tee -a "$LOG_FILE"
echo "LoRA Rank: $LORA_RANK" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Launch training in background
echo "Launching training process..." | tee -a "$LOG_FILE"

nohup python3 -m mlx_lm.lora \
    --model "$MODEL_PATH" \
    --data "$DATA_DIR" \
    --train \
    --fine-tune-type lora \
    --batch-size $BATCH_SIZE \
    --iters $ITERS \
    --learning-rate $LEARNING_RATE \
    --steps-per-report $STEPS_PER_REPORT \
    --steps-per-eval $STEPS_PER_EVAL \
    --save-every $SAVE_EVERY \
    --num-layers $NUM_LAYERS \
    --max-seq-length $MAX_SEQ_LENGTH \
    --adapter-path "$ADAPTER_PATH" \
    >> "$LOG_FILE" 2>&1 &

# Capture PID
TRAIN_PID=$!
echo $TRAIN_PID > "$PID_FILE"

echo "Training launched with PID: $TRAIN_PID" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE"
echo "PID file: $PID_FILE"
echo ""
echo "Monitor progress with:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Check process status:"
echo "  ps -p $TRAIN_PID"
echo ""
echo "Kill training if needed:"
echo "  kill $TRAIN_PID"
