#!/bin/bash
# Pre-commit hook for AGENT_TURBO
# Runs before each commit

echo "🚀 Running pre-commit checks..."

# Check if we're in the Agent Turbo workspace
if [[ "$PWD" == *"Agent_Turbo"* ]]; then
    echo "✅ Agent Turbo workspace detected"
    
    # Run Agent Turbo verification
    if command -v python3 &> /dev/null; then
        echo "🔍 Running Agent Turbo verification..."
        python3 /Volumes/DATA/Agent_Turbo/core/agent_turbo.py verify
        if [ $? -eq 0 ]; then
            echo "✅ Agent Turbo verification passed"
        else
            echo "❌ Agent Turbo verification failed"
            exit 1
        fi
    fi
    
    # Check for large files
    echo "🔍 Checking for large files..."
    large_files=$(find . -type f -size +10M -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*")
    if [ -n "$large_files" ]; then
        echo "⚠️  Large files detected:"
        echo "$large_files"
        echo "Consider using Git LFS for large files"
    fi
    
    # Check for sensitive files
    echo "🔍 Checking for sensitive files..."
    sensitive_files=$(find . -type f \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name ".env" \) -not -path "./.git/*")
    if [ -n "$sensitive_files" ]; then
        echo "❌ Sensitive files detected:"
        echo "$sensitive_files"
        echo "Please remove sensitive files before committing"
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
exit 0
