#!/bin/bash
# Configure ALPHA for replication to BETA

set -e

PG_HBA="/Library/PostgreSQL/18/data/pg_hba.conf"

echo "=== Configuring ALPHA for Replication ==="

# Add replication entry for BETA (Tailscale IP: 100.89.227.75)
echo "" | sudo tee -a $PG_HBA
echo "# Replication connections from BETA" | sudo tee -a $PG_HBA
echo "host    replication     replicator      100.89.227.75/32        scram-sha-256" | sudo tee -a $PG_HBA

echo ""
echo "Added replication entry to pg_hba.conf"

# Reload PostgreSQL to apply changes
echo ""
echo "Reloading PostgreSQL configuration..."
sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl reload -D /Library/PostgreSQL/18/data

echo ""
echo "✅ ALPHA configured for replication"
echo ""
echo "Verification:"
sudo tail -3 $PG_HBA
