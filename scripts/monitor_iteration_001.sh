#!/bin/bash
# Monitor Red Team Iteration 001
# Run on ALPHA, monitors BETA every 60 seconds
# Logs to database, displays progress

echo "="*80
echo "MONITORING RED TEAM ITERATION 001"
echo "Started: $(date)"
echo "Target: 10,000 attacks"
echo "="*80
echo ""

ITERATION=001
TARGET=10000
START_TIME=$(date +%s)

while true; do
    # Get current count
    CURRENT=$(ssh beta.local "ls /Volumes/DATA/GLADIATOR/attack_patterns/iteration_${ITERATION}/*.json 2>/dev/null | wc -l" | tr -d ' ')
    
    # Calculate metrics
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))
    
    if [ "$ELAPSED" -gt 0 ] && [ "$CURRENT" -gt 0 ]; then
        RATE=$(echo "scale=2; $CURRENT / $ELAPSED" | bc)
        REMAINING=$((TARGET - CURRENT))
        ETA=$(echo "scale=0; $REMAINING / $RATE" | bc 2>/dev/null || echo "999999")
        ETA_MIN=$((ETA / 60))
        PERCENT=$(echo "scale=1; ($CURRENT * 100) / $TARGET" | bc)
        
        echo "[$(date +%H:%M:%S)] Attacks: $CURRENT/$TARGET (${PERCENT}%) | Rate: ${RATE}/sec | ETA: ${ETA_MIN}min"
        
        # Check BETA health
        BETA_RESPONSIVE=$(ping -c 1 -W 1 beta.local >/dev/null 2>&1 && echo "OK" || echo "UNRESPONSIVE")
        
        if [ "$BETA_RESPONSIVE" != "OK" ]; then
            echo "🚨 BETA UNRESPONSIVE - POSSIBLE ISSUE"
        fi
        
        # Check if complete
        if [ "$CURRENT" -ge "$TARGET" ]; then
            echo ""
            echo "="*80
            echo "✅ ITERATION 001 COMPLETE"
            echo "="*80
            echo "Attacks generated: $CURRENT"
            echo "Time: $((ELAPSED / 60)) minutes"
            echo "Average rate: ${RATE} attacks/second"
            echo ""
            echo "Ready for Arthur's review."
            break
        fi
    fi
    
    # Check every 60 seconds
    sleep 60
done
EOF
chmod +x /Users/arthurdell/GLADIATOR/scripts/monitor_iteration_001.sh
echo "✅ Monitoring script ready"
