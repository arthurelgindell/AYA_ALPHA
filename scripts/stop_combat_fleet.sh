#!/bin/bash
# Stop all combat fleet processes

LOG_DIR="/Users/arthurdell/GLADIATOR/logs/combat_fleet"

echo "Stopping GLADIATOR Combat Fleet..."

if [ -d "$LOG_DIR" ]; then
    for pidfile in "$LOG_DIR"/process_*.pid; do
        if [ -f "$pidfile" ]; then
            PID=$(cat "$pidfile")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Stopping process $PID..."
                kill "$PID"
            else
                echo "Process $PID not running"
            fi
            rm "$pidfile"
        fi
    done
fi

# Fallback: kill any remaining combat_orchestrator_turbo processes
pkill -f "combat_orchestrator_turbo.py" 2>/dev/null || true

echo "All combat processes stopped."
