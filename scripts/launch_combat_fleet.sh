#!/bin/bash
# GLADIATOR Combat Fleet Launcher
# Launches multiple parallel combat processes with optimal BETA resource allocation

set -e

SCRIPT_DIR="/Users/arthurdell/GLADIATOR/scripts"
LOG_DIR="/Users/arthurdell/GLADIATOR/logs/combat_fleet"
PROCESSES=4  # Start with optimal configuration
ROUNDS=10    # 10 rounds per session = 10 pairs per session
SESSIONS_PER_PROCESS=233  # 233 sessions * 4 processes * 10 pairs = 9,320 pairs

# Create log directory
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "GLADIATOR COMBAT FLEET LAUNCHER"
echo "=========================================="
echo "Configuration:"
echo "  Parallel processes: $PROCESSES"
echo "  Rounds per session: $ROUNDS"
echo "  Sessions per process: $SESSIONS_PER_PROCESS"
echo "  Total pairs target: $((PROCESSES * SESSIONS_PER_PROCESS * ROUNDS))"
echo ""
echo "BETA Constraint: 4 concurrent connections (optimal)"
echo "Expected time: ~27 hours"
echo "Expected throughput: ~5.7 pairs/minute"
echo ""
echo "=========================================="
echo ""

# Launch combat processes in background
for i in $(seq 1 $PROCESSES); do
    LOG_FILE="$LOG_DIR/combat_process_${i}.log"
    echo "Launching Combat Process $i..."
    echo "  Log: $LOG_FILE"

    # Launch in background with nohup
    nohup python3 -u "$SCRIPT_DIR/combat_orchestrator_turbo.py" \
        $SESSIONS_PER_PROCESS $ROUNDS \
        > "$LOG_FILE" 2>&1 &

    PID=$!
    echo "  PID: $PID"
    echo "$PID" > "$LOG_DIR/process_${i}.pid"

    # Small delay to stagger starts
    sleep 2
done

echo ""
echo "=========================================="
echo "All $PROCESSES combat processes launched!"
echo "=========================================="
echo ""
echo "Monitor progress:"
echo "  python3 $SCRIPT_DIR/combat_monitor_turbo.py"
echo ""
echo "View process logs:"
echo "  tail -f $LOG_DIR/combat_process_*.log"
echo ""
echo "Check process status:"
echo "  ps aux | grep combat_orchestrator_turbo"
echo ""
echo "Stop all processes:"
echo "  $SCRIPT_DIR/stop_combat_fleet.sh"
echo ""
