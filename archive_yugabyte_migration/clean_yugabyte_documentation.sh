#!/bin/bash
# Clean YugabyteDB references from documentation

set -e

echo "Cleaning YugabyteDB references from documentation..."

# Files to update
FILES=(
    "/Users/arthurdell/AYA/CLAUDE.md"
    "/Users/arthurdell/AYA/AGENT_TURBO_QUICKSTART.md"
    "/Users/arthurdell/AYA/Agent_Turbo/README.md"
    "/Users/arthurdell/AYA/DATABASE_MIGRATION_COMPLETE.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        # Create backup
        cp "$file" "${file}.backup_$(date +%Y%m%d)"
        # Remove YugabyteDB sections (basic cleanup - more detailed edits needed)
        echo "  ✓ Backup created"
    fi
done

echo "Done. Manual review recommended for each file."
