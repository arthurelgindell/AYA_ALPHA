#!/bin/bash
# YugabyteDB Decommissioning Script
# Completely removes YugabyteDB from ALPHA

set -e

echo "=========================================="
echo "YugabyteDB Decommissioning"
echo "=========================================="
echo ""

# Stop processes
echo "1. Stopping YugabyteDB processes..."
pkill -f "yb-master|yb-tserver|yugabyted" 2>/dev/null || true
sleep 2
pkill -9 -f "yb-master|yb-tserver|yugabyted" 2>/dev/null || true
echo "   ✓ Processes stopped"

# Remove LaunchAgents
echo "2. Removing LaunchAgents..."
sudo launchctl unload /Library/LaunchDaemons/com.aya.yugabyte*.plist 2>/dev/null || true
sudo rm -f /Library/LaunchDaemons/com.aya.yugabyte*.plist 2>/dev/null || true
echo "   ✓ LaunchAgents removed"

# Archive installation (don't delete immediately, move to archive)
echo "3. Archiving YugabyteDB installation..."
if [ -d "/Users/arthurdell/AYA/yugabyte" ]; then
    ARCHIVE_DIR="/Users/arthurdell/AYA/archive_yugabyte_$(date +%Y%m%d)"
    mkdir -p "$ARCHIVE_DIR"
    mv /Users/arthurdell/AYA/yugabyte "$ARCHIVE_DIR/yugabyte" 2>/dev/null || true
    echo "   ✓ Installation archived to $ARCHIVE_DIR"
fi

# Archive data directory
if [ -d "/Users/arthurdell/var/data" ]; then
    if [ ! -d "$ARCHIVE_DIR" ]; then
        ARCHIVE_DIR="/Users/arthurdell/AYA/archive_yugabyte_$(date +%Y%m%d)"
        mkdir -p "$ARCHIVE_DIR"
    fi
    mv /Users/arthurdell/var/data "$ARCHIVE_DIR/var_data" 2>/dev/null || true
    echo "   ✓ Data directory archived"
fi

# Remove YUGABYTE_FAILED_MIGRATION directory
if [ -d "/Users/arthurdell/AYA/YUGABYTE_FAILED_MIGRATION" ]; then
    if [ ! -d "$ARCHIVE_DIR" ]; then
        ARCHIVE_DIR="/Users/arthurdell/AYA/archive_yugabyte_$(date +%Y%m%d)"
        mkdir -p "$ARCHIVE_DIR"
    fi
    mv /Users/arthurdell/AYA/YUGABYTE_FAILED_MIGRATION "$ARCHIVE_DIR/" 2>/dev/null || true
    echo "   ✓ Failed migration directory archived"
fi

echo ""
echo "=========================================="
echo "Decommissioning Complete"
echo "=========================================="
echo ""
echo "All YugabyteDB components archived to: $ARCHIVE_DIR"
echo "Manual cleanup: Review archived files before permanent deletion"
