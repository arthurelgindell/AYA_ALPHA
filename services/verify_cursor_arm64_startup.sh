#!/bin/bash
# STARTUP VERIFICATION: Cursor ARM64 Status
# Run on system startup to verify Cursor is ARM64
# Prime Directive: Report facts, no assumptions

CURSOR_PATH="/Applications/Cursor.app/Contents/MacOS/Cursor"
LOG_FILE="$HOME/Library/Logs/cursor_arm64_verification.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Cursor ARM64 Verification" >> "$LOG_FILE"

if [ ! -f "$CURSOR_PATH" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: Cursor not found at $CURSOR_PATH" >> "$LOG_FILE"
    exit 1
fi

ARCH=$(file "$CURSOR_PATH" | grep -o "arm64\|x86_64")

if [ "$ARCH" == "arm64" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ VERIFIED: Cursor is ARM64 native" >> "$LOG_FILE"
    exit 0
elif [ "$ARCH" == "x86_64" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ FAILED: Cursor is x86_64 (Rosetta 2)" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ACTION REQUIRED: Run /Users/arthurdell/AYA/services/fix_cursor_arm64_permanent.sh" >> "$LOG_FILE"
    
    # Send notification to user
    osascript -e 'display notification "Cursor is running under Rosetta 2. ARM64 fix needed." with title "Cursor Architecture Warning"' 2>/dev/null
    
    exit 1
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Could not determine architecture" >> "$LOG_FILE"
    exit 2
fi

