#!/bin/bash
# Add pg_hba.conf entries for BETA replication

set -e

PG_HBA="/Library/PostgreSQL/18/data/pg_hba.conf"

echo "=== Adding BETA replication entries to pg_hba.conf ==="

# Add entries for BETA (both Tailscale and Ethernet IPs)
sudo bash -c "cat >> $PG_HBA <<'PGEOF'

# BETA replication connections
hostnossl    replication     replicator      100.89.227.75/32        scram-sha-256
hostnossl    all             replicator      100.89.227.75/32        scram-sha-256
hostnossl    replication     replicator      192.168.0.20/32         scram-sha-256
hostnossl    all             replicator      192.168.0.20/32         scram-sha-256
PGEOF"

echo ""
echo "=== Reloading PostgreSQL configuration ==="
sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl reload -D /Library/PostgreSQL/18/data

echo ""
echo "=== Verifying new entries ==="
sudo tail -10 $PG_HBA

echo ""
echo "✅ BETA replication entries added"
