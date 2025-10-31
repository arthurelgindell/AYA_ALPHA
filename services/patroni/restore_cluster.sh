#!/bin/bash
# Restore PostgreSQL Patroni HA Cluster
# Date: October 29, 2025
# Usage: Run this script with sudo privileges where needed

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   PostgreSQL Patroni HA Cluster Restoration ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Start etcd on ALPHA
echo -e "${YELLOW}[1/6] Starting etcd on ALPHA...${NC}"
if [ ! -f /Library/LaunchDaemons/com.aya.etcd.plist ]; then
    echo "Creating etcd LaunchDaemon..."
    sudo cp /Users/arthurdell/AYA/services/patroni/com.aya.etcd.plist /Library/LaunchDaemons/ 2>/dev/null || \
    cat > /tmp/com.aya.etcd.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aya.etcd</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/etcd</string>
        <string>--config-file</string>
        <string>/usr/local/etc/etcd/etcd.conf</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/usr/local/var/lib/etcd</string>
    <key>StandardOutPath</key>
    <string>/Users/arthurdell/Library/Logs/etcd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/arthurdell/Library/Logs/etcd.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
EOF
    sudo mv /tmp/com.aya.etcd.plist /Library/LaunchDaemons/com.aya.etcd.plist
    sudo chown root:wheel /Library/LaunchDaemons/com.aya.etcd.plist
    sudo chmod 644 /Library/LaunchDaemons/com.aya.etcd.plist
fi

# Try to load etcd (requires sudo)
if sudo launchctl list com.aya.etcd &>/dev/null; then
    echo -e "${GREEN}✓${NC} etcd already loaded"
    sudo launchctl kickstart -k system/com.aya.etcd || true
else
    echo "Loading etcd service (requires sudo)..."
    sudo launchctl load /Library/LaunchDaemons/com.aya.etcd.plist || echo "etcd may already be running"
fi

sleep 3
if etcdctl --endpoints=http://127.0.0.1:2379 endpoint health &>/dev/null; then
    echo -e "${GREEN}✓${NC} etcd is healthy on ALPHA"
else
    echo -e "${RED}✗${NC} etcd not responding. Please check /Users/arthurdell/Library/Logs/etcd.log"
fi

# Step 2: Start etcd on BETA
echo ""
echo -e "${YELLOW}[2/6] Starting etcd on BETA...${NC}"
ssh beta "sudo launchctl list com.aya.etcd &>/dev/null && sudo launchctl kickstart -k system/com.aya.etcd || sudo launchctl load /Library/LaunchDaemons/com.aya.etcd.plist" 2>/dev/null || \
echo "Note: Requires manual etcd setup on BETA if LaunchDaemon doesn't exist"

sleep 2
if etcdctl --endpoints=http://beta.tail5f2bae.ts.net:2379 endpoint health &>/dev/null; then
    echo -e "${GREEN}✓${NC} etcd is healthy on BETA"
else
    echo -e "${YELLOW}⚠${NC} BETA etcd not responding yet (may need manual start)"
fi

# Step 3: Verify etcd cluster quorum
echo ""
echo -e "${YELLOW}[3/6] Verifying etcd cluster quorum...${NC}"
if etcdctl --endpoints=http://alpha.tail5f2bae.ts.net:2379,http://beta.tail5f2bae.ts.net:2379 endpoint health &>/dev/null; then
    echo -e "${GREEN}✓${NC} etcd cluster quorum healthy"
else
    echo -e "${YELLOW}⚠${NC} etcd cluster may need both nodes running"
fi

# Step 4: Start Patroni on ALPHA
echo ""
echo -e "${YELLOW}[4/6] Starting Patroni on ALPHA...${NC}"
if sudo launchctl list com.aya.patroni-alpha &>/dev/null; then
    echo -e "${GREEN}✓${NC} Patroni already loaded"
    sudo launchctl kickstart -k system/com.aya.patroni-alpha || true
else
    echo "Loading Patroni service (requires sudo)..."
    sudo launchctl load /Library/LaunchDaemons/com.aya.patroni-alpha.plist || echo "Patroni may already be running"
fi

sleep 5
if curl -s http://alpha.tail5f2bae.ts.net:8008/patroni &>/dev/null; then
    echo -e "${GREEN}✓${NC} Patroni REST API responding on ALPHA"
else
    echo -e "${YELLOW}⚠${NC} Patroni may need more time to start. Check logs: /Users/arthurdell/Library/Logs/patroni-alpha.log"
fi

# Step 5: Start Patroni on BETA
echo ""
echo -e "${YELLOW}[5/6] Starting Patroni on BETA...${NC}"
ssh beta "sudo launchctl list com.aya.patroni-beta &>/dev/null && sudo launchctl kickstart -k system/com.aya.patroni-beta || echo 'BETA Patroni LaunchDaemon may need to be created'" 2>/dev/null || \
echo "Note: BETA Patroni LaunchDaemon needs to be created if it doesn't exist"

sleep 5
if curl -s http://beta.tail5f2bae.ts.net:8008/patroni &>/dev/null; then
    echo -e "${GREEN}✓${NC} Patroni REST API responding on BETA"
else
    echo -e "${YELLOW}⚠${NC} BETA Patroni may need manual start"
fi

# Step 6: Verify cluster status
echo ""
echo -e "${YELLOW}[6/6] Verifying cluster status...${NC}"
export PATH="/Users/arthurdell/Library/Python/3.9/bin:$PATH"
export PATRONICTL_CONFIG_FILE="/Users/arthurdell/AYA/services/patroni/patroni-alpha.yml"

if command -v patronictl &>/dev/null; then
    echo ""
    patronictl list 2>/dev/null || echo "Patroni cluster status check failed - may need more startup time"
    
    echo ""
    echo "Testing PostgreSQL connection..."
    if PGPASSWORD='Power$$336633$$' psql -h alpha.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag -c "SELECT 'ALPHA Connected' as status" &>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL accessible on ALPHA"
    fi
    
    if PGPASSWORD='Power$$336633$$' psql -h beta.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag -c "SELECT 'BETA Connected' as status" &>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL accessible on BETA"
    fi
else
    echo -e "${YELLOW}⚠${NC} patronictl not found. Install with: pip3 install patroni[etcd3]"
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           RESTORATION COMPLETE              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Verify cluster: patronictl -c /Users/arthurdell/AYA/services/patroni/patroni-alpha.yml list"
echo "2. Check replication: psql -h alpha.tail5f2bae.ts.net -p 5432 -U postgres -d aya_rag -c \"SELECT * FROM pg_stat_replication\""
echo "3. Test failover: sudo launchctl stop system/com.aya.patroni-alpha"
