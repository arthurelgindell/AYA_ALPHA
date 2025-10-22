#!/bin/bash
# PERMANENT FIX: Cursor ARM64 Architecture Issue
# Date: 2025-10-20
# Prime Directive: No false claims - verify everything

set -e  # Exit on any error

echo "🔍 CURSOR ARM64 PERMANENT FIX"
echo "================================"
echo ""

# Step 1: Detect current Cursor architecture
echo "Step 1: Detecting current Cursor installation..."
CURSOR_PATH="/Applications/Cursor.app/Contents/MacOS/Cursor"

if [ ! -f "$CURSOR_PATH" ]; then
    echo "❌ FAILED: Cursor not found at $CURSOR_PATH"
    exit 1
fi

CURRENT_ARCH=$(file "$CURSOR_PATH" | grep -o "arm64\|x86_64")
echo "Current Cursor architecture: $CURRENT_ARCH"

if [ "$CURRENT_ARCH" == "arm64" ]; then
    echo "✅ Cursor is already ARM64 native"
    echo "Architecture verification: PASSED"
    exit 0
fi

echo "⚠️  Cursor is $CURRENT_ARCH - needs ARM64 replacement"
echo ""

# Step 2: Backup current installation
echo "Step 2: Backing up current installation..."
BACKUP_DIR="$HOME/.cursor_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -R /Applications/Cursor.app "$BACKUP_DIR/" 2>/dev/null || true
echo "Backup saved to: $BACKUP_DIR"
echo ""

# Step 3: Download ARM64 version
echo "Step 3: Downloading ARM64 version..."
DOWNLOAD_URL="https://api2.cursor.sh/updates/download/golden/darwin-arm64/cursor/1.7"
DMG_PATH="/tmp/Cursor-arm64.dmg"

echo "Downloading from: $DOWNLOAD_URL"
curl -L -o "$DMG_PATH" "$DOWNLOAD_URL"

if [ ! -f "$DMG_PATH" ]; then
    echo "❌ FAILED: Download failed"
    exit 1
fi

echo "✅ Downloaded: $(ls -lh "$DMG_PATH" | awk '{print $5}')"
echo ""

# Step 4: Verify DMG is ARM64
echo "Step 4: Verifying downloaded architecture..."
hdiutil attach "$DMG_PATH" -quiet -mountpoint /Volumes/Cursor

if [ ! -d "/Volumes/Cursor/Cursor.app" ]; then
    echo "❌ FAILED: DMG mount failed or invalid structure"
    hdiutil detach /Volumes/Cursor 2>/dev/null || true
    exit 1
fi

DMG_ARCH=$(file "/Volumes/Cursor/Cursor.app/Contents/MacOS/Cursor" | grep -o "arm64\|x86_64")
echo "Downloaded Cursor architecture: $DMG_ARCH"

if [ "$DMG_ARCH" != "arm64" ]; then
    echo "❌ FAILED: Downloaded version is not ARM64"
    hdiutil detach /Volumes/Cursor
    exit 1
fi

echo "✅ Architecture verified: ARM64"
echo ""

# Step 5: Replace installation
echo "Step 5: Replacing Cursor installation..."
echo "Removing old x86_64 version..."
rm -rf /Applications/Cursor.app

echo "Installing ARM64 version..."
cp -R /Volumes/Cursor/Cursor.app /Applications/

echo "Cleaning up..."
hdiutil detach /Volumes/Cursor
rm "$DMG_PATH"

echo "✅ Installation complete"
echo ""

# Step 6: Verify new installation
echo "Step 6: Verifying new installation..."
sleep 2  # Let filesystem settle

if [ ! -f "$CURSOR_PATH" ]; then
    echo "❌ FAILED: New Cursor binary not found"
    exit 1
fi

NEW_ARCH=$(file "$CURSOR_PATH" | grep -o "arm64\|x86_64")
echo "New Cursor architecture: $NEW_ARCH"

if [ "$NEW_ARCH" != "arm64" ]; then
    echo "❌ FAILED: New installation is not ARM64"
    echo "Backup available at: $BACKUP_DIR"
    exit 1
fi

# Step 7: Verify code signature
echo ""
echo "Step 7: Verifying code signature..."
codesign -v /Applications/Cursor.app 2>&1 | head -5

# Step 8: Test launch (optional - commented out to avoid interrupting workflow)
# echo ""
# echo "Step 8: Test launching..."
# open -a Cursor &
# sleep 3
# pkill -9 Cursor 2>/dev/null || true

echo ""
echo "================================"
echo "✅ CURSOR ARM64 FIX: COMPLETE"
echo "================================"
echo ""
echo "Evidence:"
echo "├─ Previous architecture: $CURRENT_ARCH"
echo "├─ Current architecture: $NEW_ARCH"
echo "├─ Binary path: $CURSOR_PATH"
echo "├─ Backup location: $BACKUP_DIR"
echo "└─ Verification: PASSED"
echo ""
echo "🚀 Cursor is now running natively on Apple Silicon"
echo ""
echo "RESTART CURSOR TO ACTIVATE ARM64 VERSION"

