#!/bin/bash
# Emergency Backup of Restored Database
# Created: October 29, 2025

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/Users/arthurdell/AYA/backups"
BACKUP_FILE="${BACKUP_DIR}/aya_rag_restored_${TIMESTAMP}.sql"

echo "=================================================="
echo "Creating Emergency Backup of Restored Database"
echo "Time: $(date)"
echo "=================================================="
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Backup location: $BACKUP_FILE"
echo ""
echo "Starting backup... (this may take several minutes)"

/Users/arthurdell/AYA/PostgreSQL 18 \
    -h localhost \
    -p 5432 \
    -U PostgreSQL 18 \
    -d aya_rag \
    -F c \
    -f "${BACKUP_FILE}.custom" \
    2>&1

DUMP_EXIT=$?

if [ $DUMP_EXIT -eq 0 ]; then
    BACKUP_SIZE=$(du -sh "${BACKUP_FILE}.custom" | cut -f1)
    echo ""
    echo "✅ Backup completed successfully!"
    echo "   File: ${BACKUP_FILE}.custom"
    echo "   Size: $BACKUP_SIZE"
    echo ""
    echo "Also creating plain SQL backup..."

    /Users/arthurdell/AYA/PostgreSQL 18 \
        -h localhost \
        -p 5432 \
        -U PostgreSQL 18 \
        -d aya_rag \
        -F p \
        -f "${BACKUP_FILE}" \
        2>&1

    if [ $? -eq 0 ]; then
        SQL_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
        echo "✅ Plain SQL backup completed!"
        echo "   File: ${BACKUP_FILE}"
        echo "   Size: $SQL_SIZE"
    fi
else
    echo "❌ Backup failed with exit code: $DUMP_EXIT"
    exit 1
fi

echo ""
echo "=================================================="
echo "Backup Complete"
echo "=================================================="
