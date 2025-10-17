#!/bin/bash
# Post-commit hook for AGENT_TURBO
# Runs after each commit

echo "🚀 Running post-commit actions..."

# Check if we're in the Agent Turbo workspace
if [[ "$PWD" == *"Agent_Turbo"* ]]; then
    echo "✅ Agent Turbo workspace detected"
    
    # Update Agent Turbo stats
    if command -v python3 &> /dev/null; then
        echo "📊 Updating Agent Turbo stats..."
        python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py stats > /dev/null 2>&1
    fi
    
    # Log commit information
    commit_hash=$(git rev-parse HEAD)
    commit_message=$(git log -1 --pretty=%B)
    commit_author=$(git log -1 --pretty=%an)
    commit_date=$(git log -1 --pretty=%ad)
    
    echo "📝 Commit logged:"
    echo "  Hash: $commit_hash"
    echo "  Message: $commit_message"
    echo "  Author: $commit_author"
    echo "  Date: $commit_date"
    
    # Save commit log
    log_file="/Volumes/DATA/Agent_Turbo/git_config/commit_log.json"
    if [ -f "$log_file" ]; then
        # Append to existing log
        echo "{"hash":"$commit_hash","message":"$commit_message","author":"$commit_author","date":"$commit_date"}," >> "$log_file"
    else
        # Create new log
        echo "[{"hash":"$commit_hash","message":"$commit_message","author":"$commit_author","date":"$commit_date"}]" > "$log_file"
    fi
fi

echo "✅ Post-commit actions completed"
exit 0
