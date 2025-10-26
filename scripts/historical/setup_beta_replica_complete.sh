#!/bin/bash
# Complete BETA replica setup script
# Target: /Volumes/DATA/AYA/data

set -e

DATA_DIR="/Volumes/DATA/AYA/data"
ALPHA_IP="100.106.113.76"

echo "=== BETA Replica Setup ==="
echo "Target directory: $DATA_DIR"
echo ""

# Step 1: Create data directory
echo "Step 1: Creating data directory..."
mkdir -p "$DATA_DIR"
ls -la "$DATA_DIR"

echo ""
echo "Step 2: Running pg_basebackup from ALPHA..."
echo "This will take several minutes..."

/Library/PostgreSQL/18/bin/pg_basebackup \
  -h "$ALPHA_IP" \
  -U replicator \
  -D "$DATA_DIR" \
  -P \
  -R \
  --slot=beta_slot \
  -X stream

echo ""
echo "Step 3: Verifying data directory contents..."
ls -la "$DATA_DIR" | head -20

echo ""
echo "Step 4: Checking standby.signal file..."
if [ -f "$DATA_DIR/standby.signal" ]; then
    echo "✅ standby.signal exists"
    cat "$DATA_DIR/standby.signal"
else
    echo "❌ standby.signal NOT FOUND"
    exit 1
fi

echo ""
echo "Step 5: Checking postgresql.auto.conf..."
if [ -f "$DATA_DIR/postgresql.auto.conf" ]; then
    echo "✅ postgresql.auto.conf exists"
    cat "$DATA_DIR/postgresql.auto.conf"
else
    echo "❌ postgresql.auto.conf NOT FOUND"
    exit 1
fi

echo ""
echo "✅ Base backup complete!"
echo ""
echo "Next steps:"
echo "1. Start PostgreSQL with: pg_ctl -D $DATA_DIR start"
echo "2. Or configure LaunchDaemon to use this data directory"
