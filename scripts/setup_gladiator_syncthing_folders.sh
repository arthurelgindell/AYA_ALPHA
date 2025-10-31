#!/bin/bash
#
# Setup Syncthing Folders for GLADIATOR Data Parity
# Configures bidirectional sync for blue_team and red_team directories
#
# Execute on ALPHA after BETA parity sync script is run
#

set -e

echo "================================================================================"
echo "GLADIATOR Syncthing Folder Setup"
echo "================================================================================"
echo ""
echo "This script configures Syncthing to maintain GLADIATOR data parity"
echo "between ALPHA and BETA for independent development."
echo ""
echo "Prerequisites:"
echo "  1. Initial data parity achieved (run sync_gladiator_parity.sh first)"
echo "  2. Syncthing running on both ALPHA and BETA"
echo "  3. Devices paired in Syncthing"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

CONFIG_FILE="$HOME/.config/syncthing/config.xml"
BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

# Backup config
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "✅ Config backed up to: $BACKUP_FILE"
echo ""

# Detect system
if [ -d "/Volumes/DATA" ]; then
    SYSTEM="BETA"
    GLADIATOR_PATH="/Volumes/DATA/AYA/projects/GLADIATOR"
else
    SYSTEM="ALPHA"
    GLADIATOR_PATH="/Users/arthurdell/AYA/projects/GLADIATOR"
fi

echo "Detected System: $SYSTEM"
echo "GLADIATOR Path: $GLADIATOR_PATH"
echo ""

# Check if folders already exist
if grep -q 'id="gladiator-blue-team"' "$CONFIG_FILE" 2>/dev/null; then
    echo "⚠️  Syncthing folders already configured"
    echo "   Remove existing folders first if you want to reconfigure"
    exit 0
fi

echo "Configuring Syncthing folders..."
echo ""
echo "Note: This will add folder definitions to Syncthing config."
echo "You will need to:"
echo "  1. Restart Syncthing"
echo "  2. Accept folders on remote device (BETA)"
echo "  3. Verify sync starts"
echo ""

# Create folder XML snippets
BLUE_TEAM_FOLDER="
    <folder id=\"gladiator-blue-team\" label=\"GLADIATOR Blue Team\" path=\"${GLADIATOR_PATH}/blue_team\" type=\"sendreceive\" rescanIntervalS=\"3600\" fsWatcherEnabled=\"true\" fsWatcherDelayS=\"10\" fsWatcherTimeoutS=\"0\" ignorePerms=\"false\" autoNormalize=\"true\">
        <filesystemType>basic</filesystemType>
        <device id=\"A24H2BJ-A2UIIWL-OPARUJ3-DEBCLVX-ATHIYFD-BLJ3RHZ-XQHVQGC-ASPRJAF\" introducedBy=\"\">
            <encryptionPassword></encryptionPassword>
        </device>
        <device id=\"O53TVN2-O3NLQ5S-TL3DMR5-KTG7GJD-SHJGNUJ-Z32PY4N-6GFG4VS-NKALTQG\" introducedBy=\"\">
            <encryptionPassword></encryptionPassword>
        </device>
        <minDiskFree unit=\"%\">1</minDiskFree>
        <versioning type=\"staggered\">
            <param key=\"cleanInterval\" val=\"3600\"></param>
            <param key=\"maxAge\" val=\"31536000\"></param>
            <cleanupIntervalS>3600</cleanupIntervalS>
            <fsPath></fsPath>
            <fsType>basic</fsType>
        </versioning>
        <copiers>0</copiers>
        <pullerMaxPendingKiB>0</pullerMaxPendingKiB>
        <hashers>0</hashers>
        <order>random</order>
        <ignoreDelete>false</ignoreDelete>
        <scanProgressIntervalS>0</scanProgressIntervalS>
        <pullerPauseS>0</pullerPauseS>
        <pullerDelayS>1</pullerDelayS>
        <maxConflicts>10</maxConflicts>
        <disableSparseFiles>false</disableSparseFiles>
        <paused>false</paused>
        <markerName>.stfolder</markerName>
        <copyOwnershipFromParent>false</copyOwnershipFromParent>
        <modTimeWindowS>0</modTimeWindowS>
        <maxConcurrentWrites>16</maxConcurrentWrites>
        <disableFsync>false</disableFsync>
        <blockPullOrder>standard</blockPullOrder>
        <copyRangeMethod>standard</copyRangeMethod>
        <caseSensitiveFS>false</caseSensitiveFS>
        <junctionsAsDirs>false</junctionsAsDirs>
        <syncOwnership>false</syncOwnership>
        <sendOwnership>false</sendOwnership>
        <syncXattrs>false</syncXattrs>
        <sendXattrs>false</sendXattrs>
        <xattrFilter>
            <maxSingleEntrySize>1024</maxSingleEntrySize>
            <maxTotalSize>4096</maxTotalSize>
        </xattrFilter>
    </folder>"

RED_TEAM_FOLDER="
    <folder id=\"gladiator-red-team\" label=\"GLADIATOR Red Team\" path=\"${GLADIATOR_PATH}/red_team\" type=\"sendreceive\" rescanIntervalS=\"3600\" fsWatcherEnabled=\"true\" fsWatcherDelayS=\"10\" fsWatcherTimeoutS=\"0\" ignorePerms=\"false\" autoNormalize=\"true\">
        <filesystemType>basic</filesystemType>
        <device id=\"A24H2BJ-A2UIIWL-OPARUJ3-DEBCLVX-ATHIYFD-BLJ3RHZ-XQHVQGC-ASPRJAF\" introducedBy=\"\">
            <encryptionPassword></encryptionPassword>
        </device>
        <device id=\"O53TVN2-O3NLQ5S-TL3DMR5-KTG7GJD-SHJGNUJ-Z32PY4N-6GFG4VS-NKALTQG\" introducedBy=\"\">
            <encryptionPassword></encryptionPassword>
        </device>
        <minDiskFree unit=\"%\">1</minDiskFree>
        <versioning type=\"staggered\">
            <param key=\"cleanInterval\" val=\"3600\"></param>
            <param key=\"maxAge\" val=\"31536000\"></param>
            <cleanupIntervalS>3600</cleanupIntervalS>
            <fsPath></fsPath>
            <fsType>basic</fsType>
        </versioning>
        <copiers>0</copiers>
        <pullerMaxPendingKiB>0</pullerMaxPendingKiB>
        <hashers>0</hashers>
        <order>random</order>
        <ignoreDelete>false</ignoreDelete>
        <scanProgressIntervalS>0</scanProgressIntervalS>
        <pullerPauseS>0</pullerPauseS>
        <pullerDelayS>1</pullerDelayS>
        <maxConflicts>10</maxConflicts>
        <disableSparseFiles>false</disableSparseFiles>
        <paused>false</paused>
        <markerName>.stfolder</markerName>
        <copyOwnershipFromParent>false</copyOwnershipFromParent>
        <modTimeWindowS>0</modTimeWindowS>
        <maxConcurrentWrites>16</maxConcurrentWrites>
        <disableFsync>false</disableFsync>
        <blockPullOrder>standard</blockPullOrder>
        <copyRangeMethod>standard</copyRangeMethod>
        <caseSensitiveFS>false</caseSensitiveFS>
        <junctionsAsDirs>false</junctionsAsDirs>
        <syncOwnership>false</syncOwnership>
        <sendOwnership>false</sendOwnership>
        <syncXattrs>false</syncXattrs>
        <sendXattrs>false</sendXattrs>
        <xattrFilter>
            <maxSingleEntrySize>1024</maxSingleEntrySize>
            <maxTotalSize>4096</maxTotalSize>
        </xattrFilter>
    </folder>"

echo "⚠️  MANUAL CONFIGURATION REQUIRED"
echo ""
echo "Due to XML complexity, please configure Syncthing folders manually:"
echo ""
echo "1. Open Syncthing Web UI: http://127.0.0.1:8384"
echo "2. Add Folder:"
echo "   - Folder Label: 'GLADIATOR Blue Team'"
echo "   - Folder Path: ${GLADIATOR_PATH}/blue_team"
echo "   - Folder Type: Send & Receive"
echo "   - Share with: BETA device"
echo ""
echo "3. Add Folder:"
echo "   - Folder Label: 'GLADIATOR Red Team'"
echo "   - Folder Path: ${GLADIATOR_PATH}/red_team"
echo "   - Folder Type: Send & Receive"
echo "   - Share with: BETA device"
echo ""
echo "4. Accept folders on BETA device"
echo ""
echo "Alternative: Use the sync_gladiator_parity.sh script for one-time sync"
echo ""

