#!/bin/bash

# WormGPT Preparation Script
# Prepares system for WormGPT deployment once files are downloaded

set -e

WORMGPT_DIR="/Users/arthurdell/AYA/models/wormgpt"
LM_STUDIO_MODELS="/Users/arthurdell/Library/Application Support/LM Studio/models"

echo "================================================================================
WORMGPT PREPARATION
================================================================================
"

# Check if WormGPT directory exists and has files
if [ ! -d "$WORMGPT_DIR" ]; then
    echo "❌ Error: WormGPT directory not found: $WORMGPT_DIR"
    exit 1
fi

# Count files in directory (excluding README)
FILE_COUNT=$(find "$WORMGPT_DIR" -type f ! -name "README.md" ! -name ".DS_Store" | wc -l | tr -d ' ')

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "⚠️  Warning: No model files found in $WORMGPT_DIR"
    echo "   Place WormGPT files in this directory first"
    exit 1
fi

echo "✅ Found $FILE_COUNT files in WormGPT directory"
echo ""

# Get total size
TOTAL_SIZE=$(du -sh "$WORMGPT_DIR" | cut -f1)
echo "📦 Total size: $TOTAL_SIZE"
echo ""

# List file types
echo "📄 File types found:"
find "$WORMGPT_DIR" -type f ! -name "README.md" ! -name ".DS_Store" -exec file {} \; | cut -d: -f2 | sort | uniq -c
echo ""

# Check for common model file patterns
HAS_SAFETENSORS=$(find "$WORMGPT_DIR" -name "*.safetensors" | wc -l | tr -d ' ')
HAS_BIN=$(find "$WORMGPT_DIR" -name "*.bin" | wc -l | tr -d ' ')
HAS_GGUF=$(find "$WORMGPT_DIR" -name "*.gguf" | wc -l | tr -d ' ')
HAS_CONFIG=$(find "$WORMGPT_DIR" -name "config.json" | wc -l | tr -d ' ')

echo "🔍 Model file detection:"
[ "$HAS_SAFETENSORS" -gt 0 ] && echo "  ✅ Found .safetensors files ($HAS_SAFETENSORS)"
[ "$HAS_BIN" -gt 0 ] && echo "  ✅ Found .bin files ($HAS_BIN)"
[ "$HAS_GGUF" -gt 0 ] && echo "  ✅ Found .gguf files ($HAS_GGUF)"
[ "$HAS_CONFIG" -gt 0 ] && echo "  ✅ Found config.json"
echo ""

# Verify structure
if [ "$HAS_CONFIG" -eq 0 ] && [ "$HAS_SAFETENSORS" -eq 0 ] && [ "$HAS_BIN" -eq 0 ] && [ "$HAS_GGUF" -eq 0 ]; then
    echo "⚠️  Warning: No recognized model files found"
    echo "   Expected: .safetensors, .bin, or .gguf files"
fi

echo "✅ WormGPT directory is ready"
echo ""
echo "Next steps:"
echo "1. Verify files are complete"
echo "2. Run: ./scripts/deploy_models_to_lm_studio.sh"
echo "3. Configure LM Studio to load WormGPT"
echo "4. Test adversarial generation"
echo ""

