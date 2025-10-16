#!/bin/bash
# GLADIATOR Iteration Backup Script
# Fast backup to ALPHA internal before each Red Team iteration
# Prompts Arthur for approval before proceeding

set -e

ITERATION=$1

if [ -z "$ITERATION" ]; then
    echo "Usage: $0 <iteration_number>"
    echo "Example: $0 001"
    exit 1
fi

BACKUP_ROOT="/Users/arthurdell/GLADIATOR_BACKUPS"
ITER_BACKUP="${BACKUP_ROOT}/iteration_${ITERATION}"

echo "========================================================================"
echo "GLADIATOR ITERATION ${ITERATION} - BACKUP & CHECKPOINT"
echo "========================================================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_ROOT"

# ALPHA Database Backup (FAST - local)
echo "[1/4] Backing up ALPHA database..."
pg_dump -h localhost -U postgres -d aya_rag -Fc > \
    "${ITER_BACKUP}_alpha_db.dump"
DB_SIZE=$(ls -lh "${ITER_BACKUP}_alpha_db.dump" | awk '{print $5}')
echo "✅ Database backed up: ${DB_SIZE}"

# ALPHA GLADIATOR folder (FAST - copy-on-write)
echo "[2/4] Backing up ALPHA GLADIATOR folder..."
cp -al /Users/arthurdell/GLADIATOR "${ITER_BACKUP}_alpha_gladiator"
FOLDER_SIZE=$(du -sh "${ITER_BACKUP}_alpha_gladiator" | awk '{print $1}')
echo "✅ GLADIATOR folder backed up: ${FOLDER_SIZE}"

# BETA attack patterns (NETWORK TRANSFER - 2.34 Gbps)
echo "[3/4] Backing up BETA attack patterns..."
START_TIME=$(date +%s)
rsync -av --stats \
    beta.local:/Volumes/DATA/GLADIATOR/ \
    "${ITER_BACKUP}_beta/" 2>&1 | tail -5
END_TIME=$(date +%s)
TRANSFER_TIME=$((END_TIME - START_TIME))
BETA_SIZE=$(du -sh "${ITER_BACKUP}_beta" 2>/dev/null | awk '{print $1}' || echo "0")
echo "✅ BETA backed up: ${BETA_SIZE} in ${TRANSFER_TIME}s"

# Summary
echo ""
echo "[4/4] Backup Summary"
echo "--------------------------------------------------------------------"
echo "  ALPHA DB: ${DB_SIZE}"
echo "  ALPHA folder: ${FOLDER_SIZE}"
echo "  BETA data: ${BETA_SIZE}"
echo "  Total time: ${TRANSFER_TIME} seconds"
echo "  Location: ${ITER_BACKUP}_*"
echo ""

# Log to database
psql -h localhost -U postgres -d aya_rag << SQLEOF
INSERT INTO gladiator_change_log (
    change_type, changed_by, entity_type, entity_name,
    reason, impact, metadata
) VALUES (
    'iteration_backup',
    'cursor',
    'backup',
    'iteration_${ITERATION}',
    'Pre-iteration safety backup to ALPHA internal storage',
    'critical',
    '{"backup_location": "${ITER_BACKUP}", "transfer_time_seconds": ${TRANSFER_TIME}}'::jsonb
);
SQLEOF

echo "✅ Backup logged to database"
echo ""

# CHECKPOINT: Prompt Arthur for approval
echo "========================================================================"
echo "ITERATION ${ITERATION} CHECKPOINT - AWAITING APPROVAL"
echo "========================================================================"
echo ""
echo "Backup complete. Ready to begin Red Team iteration ${ITERATION}."
echo ""
echo "⚠️  RED TEAM WILL RUN FOR SPECIFIED DURATION"
echo "⚠️  MONITORING WILL ABORT IF DANGEROUS"
echo "⚠️  BACKUP AVAILABLE FOR RESTORE IF NEEDED"
echo ""
echo "Type 'GO' to proceed with iteration ${ITERATION}: "
read -r APPROVAL

if [ "$APPROVAL" = "GO" ]; then
    echo ""
    echo "✅ APPROVED - Beginning iteration ${ITERATION}"
    echo ""
    exit 0
else
    echo ""
    echo "❌ NOT APPROVED - Iteration ${ITERATION} cancelled"
    echo ""
    exit 1
fi
EOF
chmod +x /Users/arthurdell/GLADIATOR/scripts/iteration_backup.sh
echo "✅ Backup script created: scripts/iteration_backup.sh"
