#!/bin/bash
# Pre-push hook for AGENT_TURBO
# Runs before each push

echo "🚀 Running pre-push checks..."

# Check if we're in the Agent Turbo workspace
if [[ "$PWD" == *"Agent_Turbo"* ]]; then
    echo "✅ Agent Turbo workspace detected"
    
    # Run final verification
    if command -v python3 &> /dev/null; then
        echo "🔍 Running final Agent Turbo verification..."
        python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify
        if [ $? -eq 0 ]; then
            echo "✅ Final verification passed"
        else
            echo "❌ Final verification failed"
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Uncommitted changes detected"
        echo "Please commit all changes before pushing"
        exit 1
    fi
    
    # Check for unpushed commits
    unpushed_commits=$(git log origin/$(git branch --show-current)..HEAD --oneline | wc -l)
    if [ "$unpushed_commits" -gt 0 ]; then
        echo "📤 Pushing $unpushed_commits commits"
    fi
fi

echo "✅ Pre-push checks passed"
exit 0
