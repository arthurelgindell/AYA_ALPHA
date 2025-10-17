#!/bin/bash
# AGENT_TURBO Mode Auto-Start Script
# Ensures all optimizations are available for GAMMA project

set -e

# Log startup
echo "$(date): Starting AGENT_TURBO Mode..." >> /tmp/agent-turbo.log

# 1. Create RAM disk if not exists (10GB)
if [ ! -d "/Volumes/DATA/GAMMA/AGENT_RAM" ]; then
    echo "$(date): Creating 10GB RAM disk..." >> /tmp/agent-turbo.log

    # Create RAM disk
    DISK_ID=$(hdiutil attach -nomount ram://20971520 2>/dev/null)

    if [ $? -eq 0 ]; then
        # Format the RAM disk
        diskutil erasevolume HFS+ "AGENT_RAM" $DISK_ID >/dev/null 2>&1

        # Create cache directory
        mkdir -p /Volumes/DATA/GAMMA/AGENT_RAM/cache

        # Create symlink for AGENT_TURBO
        ln -sfn /Volumes/DATA/GAMMA/AGENT_RAM/cache ~/.agent_turbo/agent_turbo_cache_ram

        echo "$(date): RAM disk created at /Volumes/DATA/GAMMA/AGENT_RAM" >> /tmp/agent-turbo.log
    else
        echo "$(date): Failed to create RAM disk" >> /tmp/agent-turbo.log
    fi
else
    echo "$(date): RAM disk already exists" >> /tmp/agent-turbo.log
fi

# 2. Initialize AGENT_TURBO with Turbo Mode
if [ -f ~/.agent_turbo/agent_turbo.py ]; then
    echo "$(date): Initializing AGENT_TURBO..." >> /tmp/agent-turbo.log

    # Check AGENT_TURBO stats
    python3 ~/.agent_turbo/agent_turbo.py stats > /tmp/agent-turbo-stats.json 2>&1

    # GAMMA system initialization complete
    echo "$(date): GAMMA AGENT_TURBO initialization complete" >> /tmp/agent-turbo.log

    # GPU accelerator initialization
    python3 ~/.agent_turbo/agent_turbo_gpu.py > /dev/null 2>&1 &

# 3. Check system connectivity
ping -c 1 -t 1 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "$(date): System connectivity OK" >> /tmp/agent-turbo.log
else
    echo "$(date): System connectivity failed" >> /tmp/agent-turbo.log
fi

# 4. Initialize Turbo Mode components
if [ -f ~/.agent_turbo/agent_turbo.py ]; then
    echo "$(date): Activating AGENT_TURBO Mode..." >> /tmp/agent-turbo.log

    # Run turbo mode in background to initialize all components
    python3 -c "
import sys
sys.path.insert(0, '/Users/arthurdell/.agent_turbo')
try:
    from agent_turbo import AgentTurbo
    turbo = AgentTurbo()
    stats = turbo.stats()
    print(f'AGENT_TURBO Mode Active: {len(stats)} entries')

    # Warm up the cache
    result = turbo.query('GAMMA initialization')
    print(f'Cache warmed up: {len(result)} characters')
except Exception as e:
    print(f'Error: {e}')
" >> /tmp/agent-turbo.log 2>&1
fi

# 5. Create status file for verification
echo "{
    \"status\": \"active\",
    \"timestamp\": \"$(date)\",
    \"ram_disk\": \"$([ -d '/Volumes/DATA/GAMMA/AGENT_RAM' ] && echo 'mounted' || echo 'not mounted')\",
    \"beta_connected\": \"$(ping -c 1 -t 1 100.84.202.68 > /dev/null 2>&1 && echo 'yes' || echo 'no')\"
}" > ~/.claude/agent_turbo_status.json

echo "$(date): AGENT_TURBO startup complete" >> /tmp/agent-turbo.log

# Keep the service healthy
exit 0
