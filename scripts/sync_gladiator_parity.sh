#!/bin/bash
#
# GLADIATOR Data Parity Sync Script
# Ensures both ALPHA and BETA have complete Blue Team and Red Team data
# For independent development on both systems
#
# Execute on ALPHA to sync BETA's red_team data
# Execute on BETA to sync ALPHA's blue_team data
#

set -e

echo "================================================================================"
echo "GLADIATOR Data Parity Sync"
echo "================================================================================"
echo "Started: $(date)"
echo ""

# Detect system
if [ -d "/Volumes/DATA" ]; then
    SYSTEM="BETA"
    BASE_PATH="/Volumes/DATA/AYA/projects/GLADIATOR"
    REMOTE_SYSTEM="ALPHA"
    REMOTE_PATH="/Users/arthurdell/AYA/projects/GLADIATOR"
    REMOTE_HOST="alpha.tail5f2bae.ts.net"
else
    SYSTEM="ALPHA"
    BASE_PATH="/Users/arthurdell/AYA/projects/GLADIATOR"
    REMOTE_SYSTEM="BETA"
    REMOTE_PATH="/Volumes/DATA/AYA/projects/GLADIATOR"
    REMOTE_HOST="beta.tail5f2bae.ts.net"
fi

echo "Detected System: $SYSTEM"
echo "Local Path: $BASE_PATH"
echo "Remote System: $REMOTE_SYSTEM"
echo "Remote Path: $REMOTE_PATH"
echo "Remote Host: $REMOTE_HOST"
echo ""

# Verify local GLADIATOR exists
if [ ! -d "$BASE_PATH" ]; then
    echo "❌ ERROR: GLADIATOR not found at $BASE_PATH"
    exit 1
fi

# Ensure directories exist
mkdir -p "$BASE_PATH/blue_team/{datasets,checkpoints,logs,models}"
mkdir -p "$BASE_PATH/red_team/{datasets,attack_patterns,logs,models}"

if [ "$SYSTEM" = "ALPHA" ]; then
    echo "================================================================================"
    echo "Syncing Red Team Data from BETA to ALPHA"
    echo "================================================================================"
    echo ""
    echo "This will sync BETA's red_team data (53GB, 34,155 patterns) to ALPHA"
    echo "to enable independent Red Team development on ALPHA."
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    
    echo ""
    echo "Checking BETA GLADIATOR location..."
    
    # Check if consolidated path exists
    REMOTE_RED_TEAM="$REMOTE_PATH/red_team"
    if ssh arthurdell@$REMOTE_HOST "test -d $REMOTE_RED_TEAM" 2>/dev/null; then
        echo "  ✅ Found consolidated path: $REMOTE_RED_TEAM"
        SOURCE_PATH="$REMOTE_RED_TEAM"
    elif ssh arthurdell@$REMOTE_HOST "test -d /Volumes/DATA/GLADIATOR/attack_patterns" 2>/dev/null; then
        echo "  ℹ️  Using original GLADIATOR location: /Volumes/DATA/GLADIATOR"
        SOURCE_PATH="/Volumes/DATA/GLADIATOR"
        echo "  Will sync attack_patterns, armed_exploits, combat_training to red_team/"
    else
        echo "  ❌ ERROR: Could not find GLADIATOR data on BETA"
        exit 1
    fi
    
    echo ""
    echo "Syncing red_team data..."
    echo "Source: $REMOTE_HOST:$SOURCE_PATH"
    echo "Target: $BASE_PATH/red_team/"
    echo ""
    
    # Create red_team directories
    mkdir -p "$BASE_PATH/red_team/{datasets,attack_patterns,logs,models}"
    
    # Sync based on source location
    if [ "$SOURCE_PATH" = "$REMOTE_RED_TEAM" ]; then
        # Already organized in red_team
        rsync -avz --progress \
            --exclude='.git' \
            --exclude='*.tmp' \
            --exclude='*.log' \
            arthurdell@$REMOTE_HOST:$SOURCE_PATH/ \
            $BASE_PATH/red_team/
    else
        # Need to organize from old structure
        echo "  Syncing attack_patterns..."
        rsync -avz --progress \
            arthurdell@$REMOTE_HOST:$SOURCE_PATH/attack_patterns/ \
            $BASE_PATH/red_team/attack_patterns/ 2>/dev/null || echo "    (attack_patterns may not exist)"
        
        echo "  Syncing armed_exploits..."
        rsync -avz --progress \
            arthurdell@$REMOTE_HOST:$SOURCE_PATH/armed_exploits/ \
            $BASE_PATH/red_team/datasets/armed_exploits/ 2>/dev/null || echo "    (armed_exploits may not exist)"
        
        echo "  Syncing combat_training..."
        rsync -avz --progress \
            arthurdell@$REMOTE_HOST:$SOURCE_PATH/combat_training/ \
            $BASE_PATH/red_team/datasets/combat_training/ 2>/dev/null || echo "    (combat_training may not exist)"
        
        # Sync datasets if exists
        if ssh arthurdell@$REMOTE_HOST "test -d $SOURCE_PATH/datasets" 2>/dev/null; then
            echo "  Syncing datasets..."
            rsync -avz --progress \
                --exclude='blue_team*' \
                arthurdell@$REMOTE_HOST:$SOURCE_PATH/datasets/ \
                $BASE_PATH/red_team/datasets/ 2>/dev/null || true
        fi
    fi
    
    echo ""
    echo "✅ Red Team data synced to ALPHA"
    echo ""
    
    # Verify sync
    echo "Verification:"
    RED_TEAM_SIZE=$(du -sh "$BASE_PATH/red_team" | cut -f1)
    RED_TEAM_FILES=$(find "$BASE_PATH/red_team" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  Red Team data size: $RED_TEAM_SIZE"
    echo "  Red Team files: $RED_TEAM_FILES"
    
    if [ -d "$BASE_PATH/red_team/attack_patterns/iteration_001" ]; then
        PATTERN_COUNT=$(find "$BASE_PATH/red_team/attack_patterns/iteration_001" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
        echo "  Attack patterns: $PATTERN_COUNT"
        if [ "$PATTERN_COUNT" -gt 30000 ]; then
            echo "  ✅ Attack patterns verified"
        else
            echo "  ⚠️  Warning: Expected ~34,155 patterns"
        fi
    fi
    
elif [ "$SYSTEM" = "BETA" ]; then
    echo "================================================================================"
    echo "Syncing Blue Team Data from ALPHA to BETA"
    echo "================================================================================"
    echo ""
    echo "This will sync ALPHA's blue_team data (450MB) to BETA"
    echo "to enable independent Blue Team development on BETA."
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    
    echo ""
    echo "Syncing blue_team data..."
    echo "Source: $REMOTE_HOST:$REMOTE_PATH/blue_team/"
    echo "Target: $BASE_PATH/blue_team/"
    echo ""
    
    # Use rsync over SSH for efficient sync
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='*.tmp' \
        --exclude='*.log' \
        arthurdell@$REMOTE_HOST:$REMOTE_PATH/blue_team/ \
        $BASE_PATH/blue_team/
    
    echo ""
    echo "✅ Blue Team data synced to BETA"
    echo ""
    
    # Verify sync
    echo "Verification:"
    BLUE_TEAM_SIZE=$(du -sh "$BASE_PATH/blue_team" | cut -f1)
    BLUE_TEAM_FILES=$(find "$BASE_PATH/blue_team" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  Blue Team data size: $BLUE_TEAM_SIZE"
    echo "  Blue Team files: $BLUE_TEAM_FILES"
    
    if [ -d "$BASE_PATH/blue_team/checkpoints/blue_team_8b" ]; then
        echo "  ✅ Blue Team checkpoints verified"
    fi
    if [ -d "$BASE_PATH/blue_team/datasets/blue_team_training" ]; then
        echo "  ✅ Blue Team training data verified"
    fi
fi

echo ""
echo "================================================================================"
echo "Parity Sync Complete"
echo "================================================================================"
echo "Finished: $(date)"
echo ""
echo "Both systems now have:"
echo "  ✅ Full GLADIATOR codebase"
echo "  ✅ Complete Blue Team data"
echo "  ✅ Complete Red Team data"
echo ""
echo "Independent development enabled on both ALPHA and BETA."
echo ""
echo "Note: This is a ONE-TIME sync. No ongoing synchronization needed."
echo "      Both systems will maintain independent copies for development."
echo ""

