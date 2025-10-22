#!/bin/bash
#
# GLADIATOR Dataset Expansion - Batch 1 Launcher
# Execute privilege escalation generation on BETA
#

echo "================================================================================"
echo "GLADIATOR Dataset Expansion - Batch 1: Privilege Escalation"
echo "================================================================================"
echo "Started: $(date)"
echo "Target: 800 samples"
echo "System: BETA (beta.local)"
echo "Model: qwen3-14b-mlx"
echo ""

# Copy script to BETA if needed
echo "Ensuring script is on BETA..."
scp /Users/arthurdell/GLADIATOR/datasets/generate_privilege_escalation_batch.py beta.local:/Volumes/DATA/GLADIATOR/datasets/ 2>/dev/null

# Launch generation on BETA in background
echo "Launching generation on BETA (background process)..."
ssh beta.local "cd /Volumes/DATA/GLADIATOR/datasets && nohup python3 generate_privilege_escalation_batch.py > generation_batch1.log 2>&1 &" 

# Get PID
sleep 2
PID=$(ssh beta.local "ps aux | grep generate_privilege_escalation | grep -v grep | awk '{print \$2}'")

if [ -n "$PID" ]; then
    echo "✅ Generation launched on BETA"
    echo "PID: $PID"
    echo "Monitor: ssh beta.local 'tail -f /Volumes/DATA/GLADIATOR/datasets/generation_batch1.log'"
else
    echo "⚠️  Could not verify process PID (may still be running)"
fi

echo ""
echo "================================================================================"
echo "Generation Details:"
echo "  Batch: Privilege Escalation (800 samples)"
echo "  Categories: 8 (100 samples each)"
echo "  Estimated Duration: 10-15 hours"
echo "  Output: /Volumes/DATA/GLADIATOR/datasets/expansion/privilege_escalation_batch1.jsonl"
echo "  Log: /Volumes/DATA/GLADIATOR/datasets/generation_batch1.log"
echo "================================================================================"
echo ""
echo "Next Actions:"
echo "1. Monitor progress: ssh beta.local 'tail -f /Volumes/DATA/GLADIATOR/datasets/generation_batch1.log'"
echo "2. Check samples: ssh beta.local 'ls -lh /Volumes/DATA/GLADIATOR/datasets/expansion/'"
echo "3. Quality review when 80+ samples generated (10%)"
echo ""
echo "Task 15 Status: LAUNCHED"
echo "================================================================================"
EOF
chmod +x /Users/arthurdell/GLADIATOR/datasets/launch_expansion_batch1.sh
cat WEEK_1_TASK_14_NETWORK_ASSESSMENT.md

