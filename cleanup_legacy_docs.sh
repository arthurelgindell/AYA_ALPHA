#!/bin/bash
# Safe cleanup of legacy documentation
# Moves dated/legacy docs to archive folder (doesn't delete)

set -e  # Exit on error

ARCHIVE_DIR="/Users/arthurdell/AYA/archive_legacy_docs"
AYA_DIR="/Users/arthurdell/AYA"

echo "=================================="
echo "AYA Legacy Documentation Cleanup"
echo "=================================="
echo ""

# Create archive directory
mkdir -p "$ARCHIVE_DIR"
echo "✅ Created archive directory: $ARCHIVE_DIR"
echo ""

# Files to KEEP (not archive)
KEEP_FILES=(
    "README.md"
    "CLAUDE.md"
    "EMBEDDING_STANDARD.md"
)

echo "Files to KEEP in AYA root:"
for file in "${KEEP_FILES[@]}"; do
    echo "  - $file"
done
echo ""

# Move dated documentation files (with dates in filenames)
echo "Moving dated documentation to archive..."
cd "$AYA_DIR"

MOVED_COUNT=0
for file in *.md; do
    # Skip if file is in KEEP list
    if [[ " ${KEEP_FILES[@]} " =~ " ${file} " ]]; then
        continue
    fi
    
    # Move to archive
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo "  ✓ Moved: $file"
        ((MOVED_COUNT++))
    fi
done

echo ""
echo "=================================="
echo "Cleanup Summary"
echo "=================================="
echo "Files moved to archive: $MOVED_COUNT"
echo "Files kept in AYA root: ${#KEEP_FILES[@]}"
echo ""

# Verification
echo "Current AYA root markdown files:"
ls -1 "$AYA_DIR"/*.md 2>/dev/null || echo "  (none)"
echo ""

echo "Archive contents:"
ls -1 "$ARCHIVE_DIR" | head -10
ARCHIVE_COUNT=$(ls -1 "$ARCHIVE_DIR" | wc -l)
echo "  ... ($ARCHIVE_COUNT total files in archive)"
echo ""

echo "✅ CLEANUP COMPLETE"
echo "Archive location: $ARCHIVE_DIR"
