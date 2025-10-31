#!/bin/bash
# GLADIATOR Adversarial Models Download Script
# Downloads models sequentially: Red Team first, then Blue Team
# Optimized for ALPHA (512GB RAM) and BETA (256GB RAM)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODELS_DIR="${1:-/Users/arthurdell/AYA/models}"
HUGGINGFACE_CACHE="${HOME}/.cache/huggingface"

# Detect system
if [[ "$(hostname)" == *"beta"* ]] || [[ -d "/Volumes/DATA/AYA" ]]; then
    SYSTEM="BETA"
    MODELS_DIR="${MODELS_DIR:-/Volumes/DATA/AYA/models}"
else
    SYSTEM="ALPHA"
    MODELS_DIR="${MODELS_DIR:-/Users/arthurdell/AYA/models}"
fi

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}GLADIATOR Adversarial Models Download${NC}"
echo -e "${BLUE}System: ${SYSTEM}${NC}"
echo -e "${BLUE}Target Directory: ${MODELS_DIR}${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""

# Create models directory
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

# Function to download from Hugging Face
download_hf_model() {
    local model_name=$1
    local local_name=$2
    local quantized=$3
    
    echo -e "${GREEN}Downloading: ${model_name}${NC}"
    echo -e "${YELLOW}Local name: ${local_name}${NC}"
    
    if [ "$quantized" = "true" ]; then
        echo -e "${YELLOW}Using quantized version (smaller, faster)${NC}"
    fi
    
    # Use huggingface-cli if available, otherwise python module, otherwise git-lfs
    if command -v huggingface-cli &> /dev/null; then
        echo "Using huggingface-cli..."
        huggingface-cli download "$model_name" \
            --local-dir "$local_name" \
            --local-dir-use-symlinks False \
            --resume-download
    elif python3 -c "import huggingface_hub" 2>/dev/null; then
        echo "Using python huggingface_hub module..."
        python3 -m huggingface_hub.commands.huggingface_cli download "$model_name" \
            --local-dir "$local_name" \
            --local-dir-use-symlinks False \
            --resume-download
    elif command -v git &> /dev/null && command -v git-lfs &> /dev/null; then
        echo "Using git-lfs..."
        git lfs install
        git clone "https://huggingface.co/${model_name}" "$local_name"
    else
        echo -e "${RED}Error: Need huggingface-hub, git-lfs, or install: pip install huggingface-hub${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ ${model_name} downloaded${NC}"
    echo ""
}

# Function to check disk space
check_space() {
    local required_gb=$1
    local available_gb=$(df -BG "$MODELS_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    
    if [ "$available_gb" -lt "$required_gb" ]; then
        echo -e "${RED}⚠️  Warning: Insufficient disk space${NC}"
        echo "Required: ${required_gb}GB, Available: ${available_gb}GB"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
}

# ============================================================================
# PHASE 1: RED TEAM MODELS
# ============================================================================

echo -e "${RED}================================================================================${NC}"
echo -e "${RED}PHASE 1: RED TEAM MODELS${NC}"
echo -e "${RED}================================================================================${NC}"
echo ""

# 1. WormGPT (Note: Manual download required)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}1. WormGPT${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  MANUAL DOWNLOAD REQUIRED${NC}"
echo ""
echo "WormGPT is not available via Hugging Face. You need to:"
echo "1. Source from dark web markets or Telegram channels"
echo "2. Download in isolated environment"
echo "3. Scan for malware/backdoors"
echo "4. Place in: ${MODELS_DIR}/wormgpt/"
echo ""
echo "Expected size: ~12GB"
echo "Expected files: Model weights, config, tokenizer"
echo ""
read -p "Have you downloaded WormGPT? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "${MODELS_DIR}/wormgpt" ]; then
        echo -e "${GREEN}✅ WormGPT found at ${MODELS_DIR}/wormgpt${NC}"
    else
        echo -e "${YELLOW}⚠️  WormGPT directory not found. Continuing with other models...${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping WormGPT for now. Can add later.${NC}"
fi
echo ""

# 2. Llama 3.1 70B Uncensored (Start with this - faster download, good capability)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}2. Llama 3.1 70B Uncensored (Red Team - Complex Attacks)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
check_space 50
download_hf_model "Undi95/Llama-3.1-70B-Uncensored" "llama-3.1-70b-uncensored"
echo ""

# 3. DeepSeek Coder 67B (Exploit Code Specialist)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}3. DeepSeek Coder 67B (Red Team - Exploit Code)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
check_space 50
download_hf_model "deepseek-ai/deepseek-coder-67b-instruct" "deepseek-coder-67b"
echo ""

# 4. Llama 3.1 405B Uncensored (Quantized for ALPHA, or native if space allows)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}4. Llama 3.1 405B Uncensored (Red Team - Maximum Reasoning)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "This is a very large model. Options:"
echo "  a) Quantized AWQ version (~120GB) - Recommended for ALPHA"
echo "  b) Native FP16 version (~240GB) - If you have space"
echo ""
read -p "Download quantized (a) or native (b)? [a] " -n 1 -r
echo
if [[ $REPLY =~ ^[Bb]$ ]]; then
    check_space 250
    download_hf_model "Undi95/Llama-3.1-405B-Uncensored" "llama-3.1-405b-uncensored"
else
    check_space 130
    download_hf_model "TheBloke/Llama-3.1-405B-Instruct-AWQ" "llama-3.1-405b-awq"
fi
echo ""

# ============================================================================
# PHASE 2: BLUE TEAM MODELS (Same as Red Team for adversarial training)
# ============================================================================

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}PHASE 2: BLUE TEAM MODELS${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""
echo "Blue Team will use the same models as Red Team for adversarial training."
echo "This ensures realistic threat simulation."
echo ""
echo -e "${GREEN}✅ All models downloaded above will be shared for Blue Team use${NC}"
echo ""

# Optional: Additional Blue Team specific models
echo -e "${YELLOW}Optional: Additional Blue Team Analysis Models${NC}"
read -p "Download additional Blue Team models? (y/n) [n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Foundation-Sec-8B (Security-focused, already have on ALPHA)
    echo -e "${YELLOW}Note: Foundation-Sec-8B already available on ALPHA${NC}"
    echo ""
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}DOWNLOAD SUMMARY${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo "Models downloaded to: ${MODELS_DIR}"
echo ""
echo "Red Team Models:"
ls -lh "$MODELS_DIR" | grep -E "llama|deepseek|wormgpt" || echo "  (checking...)"
echo ""
echo "Next Steps:"
echo "1. Configure LM Studio to load these models"
echo "2. Test model loading and inference"
echo "3. Generate initial attack patterns"
echo "4. Fine-tune with threat intelligence"
echo ""
echo -e "${GREEN}✅ Download phase complete${NC}"
echo ""

