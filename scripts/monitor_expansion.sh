#!/bin/bash
#
# GLADIATOR Dataset Expansion Monitor
# Check progress of dataset generation on BETA
#

BETA_HOST="beta.local"
EXPANSION_DIR="/Volumes/DATA/GLADIATOR/datasets/expansion"
LOG_FILE="/Volumes/DATA/GLADIATOR/datasets/generation_batch1.log"

echo "================================================================================"
echo "GLADIATOR Dataset Expansion Monitor"
echo "================================================================================"
echo "Time: $(date)"
echo ""

# Check if process is running
echo "Process Status:"
PROCESS=$(ssh $BETA_HOST "ps aux | grep generate_privilege_escalation | grep -v grep")
if [ -n "$PROCESS" ]; then
    echo "✅ Generation process RUNNING"
    PID=$(echo $PROCESS | awk '{print $2}')
    CPU=$(echo $PROCESS | awk '{print $3}')
    MEM=$(echo $PROCESS | awk '{print $4}')
    TIME=$(echo $PROCESS | awk '{print $10}')
    echo "   PID: $PID | CPU: ${CPU}% | Memory: ${MEM}% | Time: $TIME"
else
    echo "❌ Generation process NOT RUNNING"
    exit 1
fi
echo ""

# Check samples generated
echo "Dataset Progress:"
SAMPLE_COUNT=$(ssh $BETA_HOST "wc -l $EXPANSION_DIR/privilege_escalation_batch1.jsonl 2>/dev/null | awk '{print \$1}'")
if [ -n "$SAMPLE_COUNT" ] && [ "$SAMPLE_COUNT" -gt 0 ]; then
    echo "✅ Samples generated: $SAMPLE_COUNT / 800 ($(echo "scale=2; $SAMPLE_COUNT * 100 / 800" | bc)%)"
    
    # Estimate completion time
    if [ "$SAMPLE_COUNT" -gt 5 ]; then
        # Calculate average time per sample from log
        RUNTIME_SEC=$(echo $TIME | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}')
        AVG_TIME=$(echo "scale=2; $RUNTIME_SEC / $SAMPLE_COUNT" | bc)
        REMAINING=$(echo "800 - $SAMPLE_COUNT" | bc)
        ETA_SEC=$(echo "scale=0; $AVG_TIME * $REMAINING" | bc)
        ETA_HOURS=$(echo "scale=1; $ETA_SEC / 3600" | bc)
        
        echo "   Average: ${AVG_TIME}s per sample"
        echo "   Remaining: $REMAINING samples"
        echo "   ETA: ${ETA_HOURS} hours"
    fi
else
    echo "⏳ Initializing... (0 samples generated yet)"
fi
echo ""

# Check log file
echo "Recent Log Activity:"
ssh $BETA_HOST "tail -10 $LOG_FILE 2>/dev/null | grep -E 'Sample|Error|Generated|Complete' || echo '   (No relevant log entries yet)'"
echo ""

# Storage check
echo "Storage Status:"
STORAGE=$(ssh $BETA_HOST "df -h /Volumes/DATA | tail -1 | awk '{print \"Available: \" \$4 \" (\" \$5 \" used)\"}'")
echo "   $STORAGE"
echo ""

echo "================================================================================"
echo "Monitor completed: $(date)"
echo "================================================================================"
echo ""
echo "To run again: ./scripts/monitor_expansion.sh"
echo "Recommended interval: Every 2-4 hours"

