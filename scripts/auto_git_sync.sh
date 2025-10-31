#!/bin/bash
#
# Automated Git Sync Script for AYA Repository
# Syncs local changes to GitHub automatically
#
# Author: Claude for Arthur
# Date: October 29, 2025
# Usage: ./auto_git_sync.sh [--force] [--dry-run]

set -e

# Configuration
REPO_DIR="/Users/arthurdell/AYA"
LOG_FILE="/Users/arthurdell/AYA/logs/git_sync.log"
LOCK_FILE="/tmp/aya_git_sync.lock"
MAX_LOG_SIZE=$((10 * 1024 * 1024))  # 10MB

# Options
FORCE_PUSH=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_PUSH=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force] [--dry-run]"
            exit 1
            ;;
    esac
done

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Rotate log if too large
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
    log "Log rotated"
fi

# Check for lock file (prevent concurrent runs)
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        log "ERROR: Another sync is running (PID: $PID)"
        exit 1
    else
        log "Removing stale lock file"
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

log "========== Git Sync Started =========="

# Change to repo directory
cd "$REPO_DIR"

# Fetch remote changes
log "Fetching from remote..."
if ! git fetch origin 2>&1 | tee -a "$LOG_FILE"; then
    log "ERROR: Failed to fetch from remote"
    exit 1
fi

# Check if we're behind remote
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")
if [ "$BEHIND" -gt 0 ]; then
    log "WARNING: Local is $BEHIND commits behind remote"
    log "Consider running 'git pull' manually to review changes"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    log "Found uncommitted changes"
    
    if [ "$DRY_RUN" = true ]; then
        log "DRY RUN: Would commit and push the following:"
        git status --short | tee -a "$LOG_FILE"
        log "DRY RUN: Complete (no changes made)"
        exit 0
    fi
    
    # Stage all changes
    log "Staging changes..."
    git add -A
    
    # Generate commit message
    CHANGED_FILES=$(git status --short | wc -l | tr -d ' ')
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    COMMIT_MSG="Auto-sync: $CHANGED_FILES files changed at $TIMESTAMP"
    
    # Show what will be committed
    log "Changes to commit:"
    git status --short | tee -a "$LOG_FILE"
    
    # Commit
    log "Committing changes: $COMMIT_MSG"
    if ! git commit -m "$COMMIT_MSG" 2>&1 | tee -a "$LOG_FILE"; then
        log "ERROR: Failed to commit changes"
        exit 1
    fi
    
    # Push to GitHub
    log "Pushing to GitHub..."
    PUSH_CMD="git push origin main"
    if [ "$FORCE_PUSH" = true ]; then
        log "WARNING: Force push enabled"
        PUSH_CMD="git push --force-with-lease origin main"
    fi
    
    if ! eval "$PUSH_CMD" 2>&1 | tee -a "$LOG_FILE"; then
        log "ERROR: Failed to push to GitHub"
        log "You may need to pull and merge manually"
        exit 1
    fi
    
    log "SUCCESS: Changes pushed to GitHub"
else
    log "No uncommitted changes found"
fi

# Verify sync status
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    log "Repository is in sync with GitHub"
else
    log "WARNING: Local and remote commits differ"
    log "Local:  $LOCAL_COMMIT"
    log "Remote: $REMOTE_COMMIT"
fi

log "========== Git Sync Completed =========="

