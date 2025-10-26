#!/bin/bash
# Setup BETA as streaming replica of ALPHA
# Run this script on BETA

set -e

echo "=== BETA Replica Setup ==="
echo ""

# Configuration
ALPHA_HOST="100.106.113.76"  # ALPHA Tailscale IP
ALPHA_PORT="5432"
REPL_USER="replicator"
REPL_PASSWORD="Power\$\$336633\$\$"
PG_DATA="/Library/PostgreSQL/18/data"
PG_BIN="/Library/PostgreSQL/18/bin"

echo "Step 1: Backup existing data directory"
sudo mv $PG_DATA ${PG_DATA}.backup.$(date +%Y%m%d_%H%M%S)

echo ""
echo "Step 2: Create base backup from ALPHA using pg_basebackup"
echo "This will copy all data from ALPHA to BETA..."
sudo -u postgres PGPASSWORD="$REPL_PASSWORD" $PG_BIN/pg_basebackup \
  -h $ALPHA_HOST \
  -p $ALPHA_PORT \
  -U $REPL_USER \
  -D $PG_DATA \
  -Fp \
  -Xs \
  -P \
  -R

echo ""
echo "Step 3: Verify standby.signal file created"
ls -la $PG_DATA/standby.signal

echo ""
echo "Step 4: Check primary_conninfo in postgresql.auto.conf"
sudo cat $PG_DATA/postgresql.auto.conf | grep primary_conninfo

echo ""
echo "Step 5: Start PostgreSQL on BETA as replica"
sudo -u postgres $PG_BIN/pg_ctl start -D $PG_DATA -l $PG_DATA/logfile

echo ""
echo "Step 6: Wait for startup..."
sleep 5

echo ""
echo "Step 7: Verify replication status"
sudo -u postgres $PG_BIN/psql -p $ALPHA_PORT -c "SELECT * FROM pg_stat_replication;" postgres 2>/dev/null || echo "Will verify from ALPHA"

echo ""
echo "✅ BETA replica setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify replication from ALPHA"
echo "2. Check replication lag"
