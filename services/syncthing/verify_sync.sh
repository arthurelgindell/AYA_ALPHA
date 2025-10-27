#!/bin/bash
# Syncthing Sync Verification Script
# Verifies bidirectional sync between ALPHA and BETA

set -e

echo "=== SYNCTHING SYNC VERIFICATION ==="
echo ""

# Get API keys
ALPHA_API_KEY=$(cat /Users/arthurdell/.config/syncthing/config.xml | grep apikey | sed 's/.*<apikey>\(.*\)<\/apikey>.*/\1/')
BETA_API_KEY=$(ssh beta.tail5f2bae.ts.net "cat /Users/arthurdell/.config/syncthing/config.xml | grep apikey | sed 's/.*<apikey>\(.*\)<\/apikey>.*/\1/'")

echo "1. Checking Syncthing Status..."
echo "ALPHA:"
curl -s -H "X-API-Key: $ALPHA_API_KEY" 'http://localhost:8384/rest/db/status?folder=aya-unified' | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  State: {d['state']}\")
print(f\"  Files: {d['localFiles']}/{d['globalFiles']}\")
print(f\"  In Sync: {d.get('inSyncFiles', 0)}\")
print(f\"  Need: {d.get('needFiles', 0)} files\")
print(f\"  Errors: {d.get('errors', 0)}\")
"

echo ""
echo "BETA:"
ssh beta.tail5f2bae.ts.net "curl -s -H 'X-API-Key: $BETA_API_KEY' 'http://localhost:8384/rest/db/status?folder=aya-unified'" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  State: {d['state']}\")
print(f\"  Files: {d['localFiles']}/{d['globalFiles']}\")
print(f\"  In Sync: {d.get('inSyncFiles', 0)}\")
print(f\"  Need: {d.get('needFiles', 0)} files\")
print(f\"  Errors: {d.get('errors', 0)}\")
"

echo ""
echo "2. Device Connection Status..."
curl -s -H "X-API-Key: $ALPHA_API_KEY" 'http://localhost:8384/rest/system/connections' | python3 -c "
import sys, json
data = json.load(sys.stdin)
beta_conn = data['connections']['A24H2BJ-A2UIIWL-OPARUJ3-DEBCLVX-ATHIYFD-BLJ3RHZ-XQHVQGC-ASPRJAF']
print(f\"  BETA Connected: {beta_conn['connected']}\")
print(f\"  Since: {beta_conn['startedAt']}\")
print(f\"  Sent: {beta_conn['outBytesTotal']/(1024**2):.1f}MB\")
print(f\"  Received: {beta_conn['inBytesTotal']/(1024**2):.1f}MB\")
"

echo ""
echo "3. Testing Bidirectional Sync..."
TEST_FILE="/Users/arthurdell/AYA/SYNC_VERIFY_$(date +%s).txt"
echo "Test from ALPHA at $(date)" > "$TEST_FILE"

echo "  Created test file on ALPHA: $(basename $TEST_FILE)"
sleep 5

if ssh beta.tail5f2bae.ts.net "cat /Volumes/DATA/AYA/$(basename $TEST_FILE)" 2>/dev/null | grep -q "Test from ALPHA"; then
    echo "  ✅ ALPHA → BETA: WORKING"
else
    echo "  ❌ ALPHA → BETA: FAILED (file not synced within 5 seconds)"
fi

# Clean up
rm "$TEST_FILE"

echo ""
echo "=== SYNCTHING VERIFICATION COMPLETE ==="

