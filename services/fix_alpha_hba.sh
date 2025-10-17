#!/bin/bash
# Manually fix pg_hba.conf on ALPHA

set -x

PG_HBA="/Library/PostgreSQL/18/data/pg_hba.conf"

echo "=== Step 1: Show current pg_hba.conf ==="
sudo cat $PG_HBA

echo ""
echo "=== Step 2: Add replication entries ==="

sudo bash -c "cat >> $PG_HBA <<'PGEOF'

# Replication from BETA (Tailscale)
host    replication     replicator      100.89.227.75/32        md5
host    all             replicator      100.89.227.75/32        md5
PGEOF"

echo ""
echo "=== Step 3: Verify entries added ==="
sudo tail -5 $PG_HBA

echo ""
echo "=== Step 4: Reload PostgreSQL ==="
sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl reload -D /Library/PostgreSQL/18/data

echo ""
echo "=== Step 5: Test connection locally ==="
PGPASSWORD='Power$$336633$$' /Library/PostgreSQL/18/bin/psql -h 127.0.0.1 -p 5432 -U replicator -d postgres -c 'SELECT 1;'

echo ""
echo "✅ Done"
