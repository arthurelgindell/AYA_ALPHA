#!/bin/bash
# Setup environment variables for code validation
# Part of AYA Code Validation System

ENV_FILE="$HOME/.zshrc"
BACKUP_FILE="$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"

echo "🔧 Setting up code validation environment variables..."

# Backup existing .zshrc
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$BACKUP_FILE"
    echo "✅ Backed up $ENV_FILE to $BACKUP_FILE"
fi

# Check if already configured
if grep -q "CODE_VALIDATION" "$ENV_FILE" 2>/dev/null; then
    echo "⚠️  Code validation environment variables already exist"
    echo "   Updating existing values..."
    # Remove old entries
    sed -i.bak '/CODE_VALIDATION/d' "$ENV_FILE"
fi

# Add new configuration
cat >> "$ENV_FILE" << 'EOF'

# =============================================================================
# AYA Code Validation Configuration
# =============================================================================
export CODE_VALIDATION_REQUIRED=true
export CODE_VALIDATION_ENDPOINT=http://alpha.tail5f2bae.ts.net:5678/webhook/code-validate
export CODE_VALIDATION_ENFORCE=true
export CODE_VALIDATION_MODEL=qwen3-next-80b-a3b-instruct-mlx
export CODE_VALIDATION_CONCURRENT=8
EOF

echo "✅ Environment variables configured!"
echo ""
echo "Added to $ENV_FILE:"
echo "  - CODE_VALIDATION_REQUIRED=true"
echo "  - CODE_VALIDATION_ENDPOINT=http://alpha.tail5f2bae.ts.net:5678/webhook/code-validate"
echo "  - CODE_VALIDATION_ENFORCE=true"
echo "  - CODE_VALIDATION_MODEL=qwen3-next-80b-a3b-instruct-mlx"
echo "  - CODE_VALIDATION_CONCURRENT=8"
echo ""
echo "To apply immediately:"
echo "  source ~/.zshrc"
echo ""
echo "Or restart your terminal."

