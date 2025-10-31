#!/bin/bash
# Deploy downloaded models to LM Studio
# Configures models for Red Team and Blue Team use

set -e

# Detect system
if [[ "$(hostname)" == *"beta"* ]] || [[ -d "/Volumes/DATA/AYA" ]]; then
    SYSTEM="BETA"
    MODELS_DIR="/Volumes/DATA/AYA/models"
    LM_STUDIO_DIR="${HOME}/Library/Application Support/LM Studio/models"
else
    SYSTEM="ALPHA"
    MODELS_DIR="/Users/arthurdell/AYA/models"
    LM_STUDIO_DIR="${HOME}/Library/Application Support/LM Studio/models"
fi

echo "System: ${SYSTEM}"
echo "Models source: ${MODELS_DIR}"
echo "LM Studio target: ${LM_STUDIO_DIR}"

# Create LM Studio models directory
mkdir -p "$LM_STUDIO_DIR"

# Function to link model
link_model() {
    local source=$1
    local target=$2
    
    if [ -d "$source" ]; then
        echo "Linking: $(basename $source)"
        ln -sf "$source" "$target"
        echo "✅ Linked: $target"
    else
        echo "⚠️  Not found: $source"
    fi
}

# Link Red Team models
echo ""
echo "=== Linking Red Team Models ==="
link_model "${MODELS_DIR}/wormgpt" "${LM_STUDIO_DIR}/wormgpt"
link_model "${MODELS_DIR}/llama-3.1-70b-uncensored" "${LM_STUDIO_DIR}/llama-3.1-70b-uncensored"
link_model "${MODELS_DIR}/llama-3.1-405b-uncensored" "${LM_STUDIO_DIR}/llama-3.1-405b-uncensored"
link_model "${MODELS_DIR}/llama-3.1-405b-awq" "${LM_STUDIO_DIR}/llama-3.1-405b-awq"
link_model "${MODELS_DIR}/deepseek-coder-67b" "${LM_STUDIO_DIR}/deepseek-coder-67b"

echo ""
echo "✅ Models linked to LM Studio"
echo ""
echo "Next: Open LM Studio and load models"
echo "  - Red Team: Start with WormGPT or Llama 3.1 70B"
echo "  - Blue Team: Use Llama 3.1 405B for analysis"

