#!/bin/bash
# Disable PostgreSQL 18 (ARCHIVED - PostgreSQL 18 is now production)
# Run this script with: sudo bash disable_postgresql18.sh

echo "========================================"
echo "PostgreSQL 18 Shutdown Script"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   echo "❌ ERROR: This script must be run as root"
   echo "   Please run: sudo bash disable_postgresql18.sh"
   exit 1
fi

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Stopping PostgreSQL 18 service..."
echo "----------------------------------------"

# Try graceful shutdown first using pg_ctl
if [ -f "/Library/PostgreSQL/18/bin/pg_ctl" ]; then
    echo "Attempting graceful shutdown..."
    sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl stop -D /Library/PostgreSQL/18/data -m fast

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PostgreSQL 18 stopped gracefully${NC}"
    else
        echo -e "${YELLOW}⚠ Graceful shutdown failed, trying alternative method...${NC}"
    fi
fi

# Check if still running
PG_PID=$(ps aux | grep "/Library/PostgreSQL/18/bin/postgres" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$PG_PID" ]; then
    echo "PostgreSQL 18 still running (PID: $PG_PID), stopping process..."
    kill -TERM $PG_PID
    sleep 2

    # Force kill if still running
    if ps -p $PG_PID > /dev/null; then
        echo "Forcing shutdown..."
        kill -9 $PG_PID
    fi

    echo -e "${GREEN}✓ PostgreSQL 18 process stopped${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL 18 not running${NC}"
fi

echo ""
echo "Step 2: Disabling PostgreSQL 18 LaunchDaemon..."
echo "------------------------------------------------"

# Unload the LaunchDaemon
if [ -f "/Library/LaunchDaemons/postgresql-18.plist" ]; then
    echo "Unloading postgresql-18 LaunchDaemon..."
    launchctl unload /Library/LaunchDaemons/postgresql-18.plist 2>/dev/null

    # Move the plist to a backup location
    BACKUP_DIR="/Library/LaunchDaemons/disabled"
    mkdir -p "$BACKUP_DIR"

    echo "Moving postgresql-18.plist to backup location..."
    mv /Library/LaunchDaemons/postgresql-18.plist "$BACKUP_DIR/postgresql-18.plist.disabled"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ LaunchDaemon disabled and backed up to $BACKUP_DIR${NC}"
    else
        echo -e "${RED}✗ Failed to move plist file${NC}"
    fi
else
    echo -e "${YELLOW}⚠ LaunchDaemon plist not found (may already be disabled)${NC}"
fi

echo ""
echo "Step 3: Verifying PostgreSQL 18 is shut down..."
echo "------------------------------------------------"

# Check if PostgreSQL 18 is still running
PG_CHECK=$(ps aux | grep "/Library/PostgreSQL/18/bin/postgres" | grep -v grep)

if [ -z "$PG_CHECK" ]; then
    echo -e "${GREEN}✓ PostgreSQL 18 is NOT running${NC}"
else
    echo -e "${RED}✗ PostgreSQL 18 is still running!${NC}"
    echo "$PG_CHECK"
fi

# Check if port 5432 is free
PORT_CHECK=$(lsof -i :5432 | grep LISTEN)

if [ -z "$PORT_CHECK" ]; then
    echo -e "${GREEN}✓ Port 5432 is FREE${NC}"
else
    echo -e "${YELLOW}⚠ Port 5432 is still in use:${NC}"
    echo "$PORT_CHECK"
fi

echo ""
echo "Step 4: Verifying PostgreSQL 18 is running..."
echo "-------------------------------------------"

# Check PostgreSQL 18 on port 5433
PostgreSQL 18 -i :5432 | grep LISTEN)

if [ ! -z "$PostgreSQL 18" ]; then
    echo -e "${GREEN}✓ PostgreSQL 18 is running on port 5433${NC}"

    # Test connection
    if command -v psql &> /dev/null; then
        echo "Testing PostgreSQL 18 connection..."
        PGPASSWORD='Power$$336633$$' psql -h localhost -p 5433 -U postgres -d aya_rag -c "SELECT version();" > /dev/null 2>&1

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ PostgreSQL 18 connection successful${NC}"
        else
            echo -e "${YELLOW}⚠ PostgreSQL 18 connection failed (check credentials)${NC}"
        fi
    fi
else
    echo -e "${RED}✗ PostgreSQL 18 is NOT running on port 5433${NC}"
fi

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo ""
echo "PostgreSQL 18:"
if [ -z "$PG_CHECK" ]; then
    echo -e "  Status: ${GREEN}STOPPED${NC}"
else
    echo -e "  Status: ${RED}RUNNING${NC}"
fi

if [ -f "/Library/LaunchDaemons/postgresql-18.plist" ]; then
    echo -e "  Startup: ${YELLOW}ENABLED${NC} (will start on boot)"
else
    echo -e "  Startup: ${GREEN}DISABLED${NC} (will NOT start on boot)"
fi

echo ""
echo "PostgreSQL 18:"
if [ ! -z "$PostgreSQL 18" ]; then
    echo -e "  Status: ${GREEN}RUNNING${NC}"
    echo -e "  Port: ${GREEN}5433${NC}"
    echo -e "  Database: ${GREEN}aya_rag${NC}"
else
    echo -e "  Status: ${RED}NOT RUNNING${NC}"
fi

echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo ""
echo "1. PostgreSQL 18 is now dormant and will NOT start on boot"
echo "2. PostgreSQL 18 is the new default database"
echo "3. All connections should now use port 5433"
echo ""
echo "To restore PostgreSQL 18 (if needed):"
echo "  sudo mv $BACKUP_DIR/postgresql-18.plist.disabled /Library/LaunchDaemons/postgresql-18.plist"
echo "  sudo launchctl load /Library/LaunchDaemons/postgresql-18.plist"
echo ""
echo "✓ Complete!"
echo ""
