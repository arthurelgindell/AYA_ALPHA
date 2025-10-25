#!/bin/bash

# PostgreSQL Remote Access Configuration Script
# Adds BETA Tailscale IP to pg_hba.conf for K3s cluster deployment

echo "=== PostgreSQL Remote Access Configuration ==="
echo ""
echo "BETA IP: 100.84.202.68"
echo "Configuring PostgreSQL 18 to allow remote connections..."
echo ""

# Backup current pg_hba.conf
echo "Creating backup of pg_hba.conf..."
sudo cp /Library/PostgreSQL/18/data/pg_hba.conf /Library/PostgreSQL/18/data/pg_hba.conf.backup.$(date +%Y%m%d_%H%M%S)

# Add Tailscale subnet entry to pg_hba.conf
echo "Adding Tailscale subnet (100.64.0.0/10) to pg_hba.conf..."
echo "host    all             all             100.64.0.0/10           scram-sha-256" | sudo tee -a /Library/PostgreSQL/18/data/pg_hba.conf

# Reload PostgreSQL configuration
echo "Reloading PostgreSQL configuration..."
sudo /Library/PostgreSQL/18/bin/pg_ctl reload -D /Library/PostgreSQL/18/data

echo ""
echo "✅ Configuration complete!"
echo ""
echo "Added entry: host    all    all    100.64.0.0/10    scram-sha-256"
echo ""
echo "This allows all Tailscale devices to connect to PostgreSQL."

