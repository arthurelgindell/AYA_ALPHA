#!/bin/bash
# Real-time sync from ALPHA to BETA (unified AYA structure)
# Runs continuously, syncs on file changes

ALPHA_PATH="/Users/arthurdell/AYA/"
BETA_PATH="beta.tail5f2bae.ts.net:/Volumes/DATA/AYA/"

echo "=== AYA Sync Service Starting ==="
echo "ALPHA: $ALPHA_PATH"
echo "BETA:  $BETA_PATH"
echo ""

# Initial sync
echo "Performing initial sync..."
rsync -avz --delete \
  --exclude 'Databases/*.db' \
  --exclude 'Databases/*.sqlite' \
  --exclude 'backups/' \
  --exclude '*.log' \
  --exclude 'logs/' \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude 'node_modules/' \
  --exclude '.DS_Store' \
  --exclude '.venv/' \
  --exclude 'models/' \
  --exclude 'postgresql/' \
  "$ALPHA_PATH" "$BETA_PATH"

echo "✅ Initial sync complete"
echo ""
echo "Watching for changes (fswatch)..."

# Watch for changes and sync
fswatch -0 -r -e '\.log$' -e '__pycache__' -e '\.DS_Store' -e '\.git/' "$ALPHA_PATH" | while read -d "" event; do
  echo "[$(date '+%H:%M:%S')] Change detected: $event"
  rsync -avz --delete \
    --exclude 'Databases/*.db' \
    --exclude 'Databases/*.sqlite' \
    --exclude 'backups/' \
    --exclude '*.log' \
    --exclude 'logs/' \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude 'node_modules/' \
    --exclude '.DS_Store' \
    --exclude '.venv/' \
    --exclude 'models/' \
    --exclude 'postgresql/' \
    "$ALPHA_PATH" "$BETA_PATH" 2>&1 | grep -v "uptodate"
  echo "✅ Synced"
done

