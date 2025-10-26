#!/bin/bash
# Setup BETA as streaming replica of ALPHA
# Run this script on BETA with sudo password: Power

set -e

echo "=== BETA Replica Setup ==="

# Stop PostgreSQL if running
echo "Step 1: Stop PostgreSQL (if running)"
sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl stop -D /Library/PostgreSQL/18/data -m fast 2>/dev/null || echo "PostgreSQL not running"

# Backup existing data directory
echo ""
echo "Step 2: Backup existing data directory"
if [ -d /Library/PostgreSQL/18/data ]; then
    sudo mv /Library/PostgreSQL/18/data /Library/PostgreSQL/18/data.backup.$(date +%Y%m%d_%H%M%S)
    echo "Backed up existing data directory"
else
    echo "No existing data directory"
fi

# Create base backup from ALPHA
echo ""
echo "Step 3: Create base backup from ALPHA (this will take a minute...)"
sudo -u postgres bash -c "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/pg_basebackup \
  -h 100.106.113.76 \
  -p 5432 \
  -U replicator \
  -D /Library/PostgreSQL/18/data \
  -Fp \
  -Xs \
  -P \
  -R"

# Verify standby.signal created
echo ""
echo "Step 4: Verify standby.signal exists"
ls -la /Library/PostgreSQL/18/data/standby.signal

# Start PostgreSQL as replica
echo ""
echo "Step 5: Start PostgreSQL as replica"
sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl start -D /Library/PostgreSQL/18/data -l /Library/PostgreSQL/18/data/logfile

# Wait for startup
echo ""
echo "Step 6: Wait for startup (5 seconds)..."
sleep 5

# Check if running
echo ""
echo "Step 7: Verify PostgreSQL is running"
ps aux | grep postgres | grep -v grep | head -5

echo ""
echo "✅ BETA replica setup complete!"
echo ""
echo "To verify replication, run on ALPHA:"
echo "PGPASSWORD='Power\$\$336633\$\$' /Library/PostgreSQL/18/bin/psql -U postgres -c 'SELECT * FROM pg_stat_replication;'"
