#!/bin/bash
# BETA AGENT_TURBO Startup Script
set -e

echo "Sat Sep 27 22:41:30 +04 2025: Starting BETA AGENT_TURBO Mode..." >> /tmp/beta-agent-turbo.log

# Check if RAM disk exists
if [ ! -d "/Volumes/DATA/Agent_RAM" ]; then
    echo "Sat Sep 27 22:41:30 +04 2025: Creating RAM disk directories..." >> /tmp/beta-agent-turbo.log
    mkdir -p /Volumes/DATA/Agent_RAM/cache/{queries,embeddings,patterns,sessions,temp}
fi

# Initialize BETA AGENT_TURBO
if [ -f /Volumes/DATA/Agent_Turbo/core/agent_turbo.py ]; then
    echo "Sat Sep 27 22:41:30 +04 2025: Initializing BETA AGENT_TURBO..." >> /tmp/beta-agent-turbo.log
    python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats > /tmp/beta-agent-turbo-stats.json 2>&1
    echo "Sat Sep 27 22:41:30 +04 2025: BETA AGENT_TURBO initialization complete" >> /tmp/beta-agent-turbo.log
fi

# Test connectivity
ping -c 1 -t 1 8.8.8.8 > /dev/null 2>&1 && echo "Sat Sep 27 22:41:30 +04 2025: System connectivity OK" >> /tmp/beta-agent-turbo.log
ping -c 1 -t 1 100.106.170.128 > /dev/null 2>&1 && echo "Sat Sep 27 22:41:30 +04 2025: ALPHA connectivity OK" >> /tmp/beta-agent-turbo.log

echo "Sat Sep 27 22:41:30 +04 2025: BETA AGENT_TURBO startup complete" >> /tmp/beta-agent-turbo.log
exit 0

