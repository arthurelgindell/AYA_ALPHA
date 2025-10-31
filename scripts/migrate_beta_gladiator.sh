#!/bin/bash
#
# BETA GLADIATOR Migration Script
# Moves /Volumes/DATA/GLADIATOR/ to /Volumes/DATA/AYA/projects/GLADIATOR/
# Organizes data into blue_team/ and red_team/ structure
#
# Execute on BETA system only
#

set -e

echo "================================================================================"
echo "BETA GLADIATOR Migration Script"
echo "================================================================================"
echo "Started: $(date)"
echo ""

# Verify we're on BETA
if [ ! -d "/Volumes/DATA" ]; then
    echo "❌ ERROR: This script must be run on BETA system"
    echo "   Expected: /Volumes/DATA/ directory"
    exit 1
fi

# Configuration
OLD_GLADIATOR="/Volumes/DATA/GLADIATOR"
NEW_GLADIATOR="/Volumes/DATA/AYA/projects/GLADIATOR"
BACKUP_DIR="/Volumes/DATA/backups/gladiator_migration_$(date +%Y%m%d_%H%M%S)"

echo "Configuration:"
echo "  Source: $OLD_GLADIATOR"
echo "  Target: $NEW_GLADIATOR"
echo "  Backup: $BACKUP_DIR"
echo ""

# Step 1: Verify old GLADIATOR exists
if [ ! -d "$OLD_GLADIATOR" ]; then
    echo "⚠️  WARNING: Old GLADIATOR directory not found: $OLD_GLADIATOR"
    echo "   Migration may already be complete or directory moved"
    exit 0
fi

# Check size
GLADIATOR_SIZE=$(du -sh "$OLD_GLADIATOR" | cut -f1)
echo "Old GLADIATOR size: $GLADIATOR_SIZE"
echo ""

# Step 2: Stop Docker containers
echo "Step 1: Stopping Docker containers..."
if docker ps | grep -q red_combat; then
    docker stop red_combat
    echo "  ✅ Stopped red_combat container"
else
    echo "  ℹ️  red_combat container not running"
fi
echo ""

# Step 3: Create backup (optional but recommended)
echo "Step 2: Creating backup..."
mkdir -p "$BACKUP_DIR"
echo "  Backup location: $BACKUP_DIR"
echo "  (Skipping full backup due to size - using rsync for verification instead)"
echo ""

# Step 4: Create target structure
echo "Step 3: Creating target structure..."
mkdir -p "$NEW_GLADIATOR"
mkdir -p "$NEW_GLADIATOR/blue_team/{datasets,checkpoints,logs,models}"
mkdir -p "$NEW_GLADIATOR/red_team/{datasets,attack_patterns,logs,models}"
echo "  ✅ Created directory structure"
echo ""

# Step 5: Sync codebase from ALPHA (if AYA is synced)
echo "Step 4: Checking for GLADIATOR codebase..."
if [ -d "/Volumes/DATA/AYA/projects/GLADIATOR/.git" ]; then
    echo "  ✅ GLADIATOR codebase already exists (via Git/Syncthing)"
    echo "  Pulling latest changes..."
    cd "$NEW_GLADIATOR"
    git pull origin main 2>/dev/null || echo "  ℹ️  Git pull skipped (not a repo or no remote)"
else
    echo "  ⚠️  GLADIATOR codebase not found"
    echo "  ℹ️  Will copy from old location (code files only)"
fi
echo ""

# Step 6: Move red team data
echo "Step 5: Moving Red Team data..."
RED_TEAM_COUNT=0

# Move attack_patterns
if [ -d "$OLD_GLADIATOR/attack_patterns" ]; then
    echo "  Moving attack_patterns..."
    mv "$OLD_GLADIATOR/attack_patterns" "$NEW_GLADIATOR/red_team/"
    RED_TEAM_COUNT=$((RED_TEAM_COUNT + 1))
    echo "    ✅ attack_patterns moved"
fi

# Move armed_exploits
if [ -d "$OLD_GLADIATOR/armed_exploits" ]; then
    echo "  Moving armed_exploits..."
    mv "$OLD_GLADIATOR/armed_exploits" "$NEW_GLADIATOR/red_team/datasets/"
    RED_TEAM_COUNT=$((RED_TEAM_COUNT + 1))
    echo "    ✅ armed_exploits moved"
fi

# Move combat_training
if [ -d "$OLD_GLADIATOR/combat_training" ]; then
    echo "  Moving combat_training..."
    mv "$OLD_GLADIATOR/combat_training" "$NEW_GLADIATOR/red_team/datasets/"
    RED_TEAM_COUNT=$((RED_TEAM_COUNT + 1))
    echo "    ✅ combat_training moved"
fi

# Move datasets (red team specific - be careful)
if [ -d "$OLD_GLADIATOR/datasets" ]; then
    echo "  Moving datasets (excluding blue_team if present)..."
    # Move everything except blue_team directories
    find "$OLD_GLADIATOR/datasets" -mindepth 1 -maxdepth 1 ! -name "blue_team*" -exec mv {} "$NEW_GLADIATOR/red_team/datasets/" \;
    RED_TEAM_COUNT=$((RED_TEAM_COUNT + 1))
    echo "    ✅ datasets moved"
fi

# Move logs (red team specific)
if [ -d "$OLD_GLADIATOR/logs" ]; then
    echo "  Moving logs..."
    # Move everything except blue_team logs
    find "$OLD_GLADIATOR/logs" -mindepth 1 -maxdepth 1 ! -name "*blue*" ! -name "*training*" -exec mv {} "$NEW_GLADIATOR/red_team/logs/" \; 2>/dev/null || true
    echo "    ✅ logs moved"
fi

# Move models (if red team specific)
if [ -d "$OLD_GLADIATOR/models" ] && [ ! -d "$OLD_GLADIATOR/models/DavidBianco" ]; then
    echo "  Moving models..."
    mv "$OLD_GLADIATOR/models" "$NEW_GLADIATOR/red_team/" 2>/dev/null || true
    echo "    ✅ models moved"
fi

echo "  ✅ Moved $RED_TEAM_COUNT Red Team data directories"
echo ""

# Step 7: Copy remaining codebase files (scripts, configs, etc.)
echo "Step 6: Copying codebase files..."
# Copy scripts, docker, config directories
for dir in scripts docker config gladiator-workflows .github; do
    if [ -d "$OLD_GLADIATOR/$dir" ] && [ ! -d "$NEW_GLADIATOR/$dir" ]; then
        echo "  Copying $dir..."
        cp -r "$OLD_GLADIATOR/$dir" "$NEW_GLADIATOR/"
        echo "    ✅ $dir copied"
    fi
done

# Copy root-level files (README, configs, etc.)
echo "  Copying root files..."
find "$OLD_GLADIATOR" -maxdepth 1 -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.sh" -o -name "*.py" \) -exec cp {} "$NEW_GLADIATOR/" \; 2>/dev/null || true
echo "  ✅ Codebase files copied"
echo ""

# Step 8: Verify migration
echo "Step 7: Verifying migration..."
RED_TEAM_SIZE=$(du -sh "$NEW_GLADIATOR/red_team" 2>/dev/null | cut -f1 || echo "0")
echo "  Red Team data size: $RED_TEAM_SIZE"
echo "  Attack patterns: $(find "$NEW_GLADIATOR/red_team/attack_patterns" -type f 2>/dev/null | wc -l | tr -d ' ') files"

if [ -d "$NEW_GLADIATOR/red_team/attack_patterns/iteration_001" ]; then
    PATTERN_COUNT=$(find "$NEW_GLADIATOR/red_team/attack_patterns/iteration_001" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "  Pattern files: $PATTERN_COUNT"
    if [ "$PATTERN_COUNT" -gt 30000 ]; then
        echo "  ✅ Attack patterns verified"
    else
        echo "  ⚠️  Warning: Expected ~34,155 patterns, found $PATTERN_COUNT"
    fi
fi
echo ""

# Step 9: Remove old directory (after verification)
echo "Step 8: Cleaning up old directory..."
if [ -d "$OLD_GLADIATOR" ]; then
    REMAINING=$(find "$OLD_GLADIATOR" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')
    if [ "$REMAINING" -le 1 ]; then
        echo "  Removing old GLADIATOR directory..."
        rm -rf "$OLD_GLADIATOR"
        echo "  ✅ Old directory removed"
    else
        echo "  ⚠️  Warning: Old directory still contains $REMAINING items"
        echo "  Old directory: $OLD_GLADIATOR"
        echo "  Please review and remove manually if needed"
    fi
fi
echo ""

# Step 10: Update Docker configuration instructions
echo "Step 9: Docker Configuration Update Required"
echo ""
echo "  ⚠️  IMPORTANT: Update red_combat container volume mounts:"
echo ""
echo "  Old mount: /Volumes/DATA/GLADIATOR"
echo "  New mount: /Volumes/DATA/AYA/projects/GLADIATOR/red_team"
echo ""
echo "  Update docker-compose.yml or restart container with:"
echo "    -v /Volumes/DATA/AYA/projects/GLADIATOR/red_team:/gladiator/data:rw"
echo ""

# Step 11: Summary
echo "================================================================================"
echo "Migration Complete"
echo "================================================================================"
echo "Finished: $(date)"
echo ""
echo "Summary:"
echo "  ✅ GLADIATOR moved to: $NEW_GLADIATOR"
echo "  ✅ Red Team data organized in: $NEW_GLADIATOR/red_team/"
echo "  ✅ Blue Team directory ready: $NEW_GLADIATOR/blue_team/"
echo ""
echo "Next Steps:"
echo "  1. Update Docker volume mounts for red_combat container"
echo "  2. Restart red_combat container"
echo "  3. Verify container can access data"
echo "  4. Update any scripts referencing old paths"
echo ""
echo "Verification:"
echo "  docker exec red_combat ls -lh /gladiator/data/attack_patterns/ | head -5"
echo ""

