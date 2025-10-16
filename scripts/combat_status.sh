#!/bin/bash
# GLADIATOR Combat Fleet Status Dashboard

echo "=========================================="
echo "GLADIATOR COMBAT FLEET STATUS"
echo "=========================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check processes
echo "--- COMBAT PROCESSES ---"
PROCESS_COUNT=$(ps aux | grep "[c]ombat_orchestrator_turbo" | wc -l | tr -d ' ')
echo "Active processes: $PROCESS_COUNT/4"
ps aux | grep "[c]ombat_orchestrator_turbo" | awk '{print "  PID " $2 ": CPU " $3 "% | MEM " $4 "%"}'
echo ""

# Check monitor
echo "--- MONITORING ---"
MONITOR_COUNT=$(ps aux | grep "[c]ombat_monitor_turbo" | wc -l | tr -d ' ')
if [ "$MONITOR_COUNT" -gt 0 ]; then
    echo "Monitor: RUNNING"
else
    echo "Monitor: NOT RUNNING"
fi
echo ""

# Check BETA tunnel
echo "--- BETA SSH TUNNEL ---"
TUNNEL_COUNT=$(ps aux | grep "[s]sh -L 1235" | wc -l | tr -d ' ')
if [ "$TUNNEL_COUNT" -gt 0 ]; then
    echo "SSH Tunnel: ACTIVE"
    ps aux | grep "[s]sh -L 1235" | awk '{print "  PID " $2}'
else
    echo "SSH Tunnel: DOWN (CRITICAL!)"
fi
echo ""

# Count training pairs
echo "--- TRAINING DATA ---"
python3 -c "
import json
import glob
import os

path = '/Users/arthurdell/GLADIATOR/datasets/combat_training'
total_pairs = 0
valid_files = 0

for f in glob.glob(os.path.join(path, 'combat_session_*.json')):
    if os.path.getsize(f) > 1000:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                pairs = 0
                if isinstance(data, dict):
                    if 'rounds' in data:
                        pairs = len(data['rounds'])
                    elif 'training_pairs' in data:
                        pairs = len(data['training_pairs'])
                    elif 'attacks' in data:
                        pairs = len(data['attacks'])
                if pairs > 0:
                    total_pairs += pairs
                    valid_files += 1
        except:
            pass

target = 10000
remaining = target - total_pairs
progress = (total_pairs / target) * 100

print(f'Total pairs: {total_pairs:,} / {target:,} ({progress:.1f}%)')
print(f'Remaining: {remaining:,} pairs')
print(f'Valid files: {valid_files}')
"
echo ""

# Recent logs
echo "--- RECENT ACTIVITY (Process 1) ---"
tail -5 /Users/arthurdell/GLADIATOR/logs/combat_fleet/combat_process_1.log 2>/dev/null | grep -E "⚔️|✅|SESSION" || echo "  No recent activity"
echo ""

# Check for errors
echo "--- ERROR CHECK ---"
ERROR_COUNT=$(grep -c "failed\|error\|timeout" /Users/arthurdell/GLADIATOR/logs/combat_fleet/*.log 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
if [ -z "$ERROR_COUNT" ]; then
    ERROR_COUNT=0
fi
echo "Total errors in logs: $ERROR_COUNT"

if [ "$ERROR_COUNT" -gt 100 ]; then
    echo "  WARNING: High error rate detected!"
    echo "  Check logs: tail -f /Users/arthurdell/GLADIATOR/logs/combat_fleet/*.log"
fi

echo ""
echo "=========================================="
echo "Commands:"
echo "  Monitor: python3 /Users/arthurdell/GLADIATOR/scripts/combat_monitor_turbo.py"
echo "  Logs: tail -f /Users/arthurdell/GLADIATOR/logs/combat_fleet/*.log"
echo "  Stop: /Users/arthurdell/GLADIATOR/scripts/stop_combat_fleet.sh"
echo "=========================================="
