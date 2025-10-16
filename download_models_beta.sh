#!/bin/bash
# GLADIATOR MLX Models Download Script - BETA System
# Date: October 10, 2025
# Target: /Volumes/DATA/GLADIATOR/models/
# Estimated Time: 45-90 minutes
# Estimated Size: ~45GB

set -e  # Exit on error

echo "========================================================================"
echo "GLADIATOR Phase 0 - MLX Models Download"
echo "System: BETA.local"
echo "Target: /Volumes/DATA/GLADIATOR/models/"
echo "========================================================================"
echo ""

# Check if running on BETA
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" != "BETA.local" ]]; then
    echo "⚠️  WARNING: This script should run on BETA.local"
    echo "Current hostname: $HOSTNAME"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check storage space
AVAILABLE=$(df -h /Volumes/DATA | tail -1 | awk '{print $4}')
echo "✅ Storage available: $AVAILABLE"
echo ""

# Install Hugging Face CLI if needed
echo "[1/5] Checking Hugging Face CLI..."
if ! command -v huggingface-cli &> /dev/null; then
    echo "Installing huggingface-cli..."
    pip3 install --upgrade huggingface-hub --break-system-packages
    echo "✅ Installed"
else
    echo "✅ Already installed"
fi
echo ""

# Create directory structure
echo "[2/5] Creating directory structure..."
mkdir -p /Volumes/DATA/GLADIATOR/models
cd /Volumes/DATA/GLADIATOR/models
echo "✅ Created: /Volumes/DATA/GLADIATOR/models/"
echo ""

# Download models
echo "========================================================================"
echo "STARTING DOWNLOADS (~45GB total)"
echo "========================================================================"
echo ""

# Model 1: Llama 70B (Strategic Planning)
echo "[3/5] Downloading Llama-3.3-70B-Instruct-4bit (~40GB)"
echo "Purpose: Red Team strategic attack planning"
echo "ETA: 30-60 minutes (depending on connection)"
echo ""
huggingface-cli download mlx-community/Llama-3.3-70B-Instruct-4bit \
    --local-dir llama-70b-red-team \
    --quiet
echo "✅ Llama 70B downloaded: $(du -sh llama-70b-red-team | awk '{print $1}')"
echo ""

# Model 2: CodeLlama 7B (Exploit Synthesis)
echo "[4/5] Downloading CodeLlama-7b-Python-mlx (~4GB)"
echo "Purpose: Exploit code and payload generation"
echo "ETA: 5-10 minutes"
echo ""
huggingface-cli download mlx-community/CodeLlama-7b-Python-mlx \
    --local-dir codellama-7b-exploit-synthesis \
    --quiet
echo "✅ CodeLlama 7B downloaded: $(du -sh codellama-7b-exploit-synthesis | awk '{print $1}')"
echo ""

# Model 3: TinyLlama 1.1B (Attack Specialists)
echo "[5/5] Downloading TinyLlama-1.1B-Chat-v1.0-4bit (~0.7GB)"
echo "Purpose: Specialized attack generation (15 instances)"
echo "ETA: 1-2 minutes"
echo ""
huggingface-cli download mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit \
    --local-dir tinyllama-1.1b-specialist \
    --quiet
echo "✅ TinyLlama 1.1B downloaded: $(du -sh tinyllama-1.1b-specialist | awk '{print $1}')"
echo ""

# Summary
echo "========================================================================"
echo "DOWNLOAD COMPLETE"
echo "========================================================================"
echo ""
echo "Downloaded Models:"
ls -lh /Volumes/DATA/GLADIATOR/models/
echo ""

echo "Total Size:"
du -sh /Volumes/DATA/GLADIATOR/models/
echo ""

echo "Storage Remaining:"
df -h /Volumes/DATA | tail -1
echo ""

echo "========================================================================"
echo "NEXT STEPS:"
echo "========================================================================"
echo ""
echo "1. Validate models with inference tests"
echo "2. Report back to ALPHA"
echo "3. Proceed with Phase 0 Red Team generation setup"
echo ""
echo "To test models, run:"
echo "  cd /Volumes/DATA/GLADIATOR/models/llama-70b-red-team"
echo "  python3 -m mlx_lm.generate --model . --prompt 'Generate attack' --max-tokens 50"
echo ""
echo "✅ BETA MODELS READY FOR PHASE 0"
echo ""

