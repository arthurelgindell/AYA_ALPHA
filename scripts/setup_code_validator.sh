#!/bin/bash
#
# Setup Code Validator for all AYA nodes
# Configures automatic code review using ALPHA's LM Studio via Tailscale
#
# Author: Claude for Arthur
# Date: October 29, 2025

set -e

echo "=== AYA Code Validator Setup ==="
echo ""

# Detect current node
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"alpha"* ]] || [[ "$HOSTNAME" == *"ALPHA"* ]]; then
    NODE="ALPHA"
    USE_LOCAL=true
elif [[ "$HOSTNAME" == *"beta"* ]] || [[ "$HOSTNAME" == *"BETA"* ]]; then
    NODE="BETA"
    USE_LOCAL=false
elif [[ "$HOSTNAME" == *"gamma"* ]] || [[ "$HOSTNAME" == *"GAMMA"* ]]; then
    NODE="GAMMA"
    USE_LOCAL=false
else
    NODE="AIR"
    USE_LOCAL=false
fi

echo "Detected node: $NODE"
echo "Will use: $([ "$USE_LOCAL" = true ] && echo "localhost (fastest)" || echo "Tailscale (cross-node)")"
echo ""

# Make validator executable
chmod +x /Users/arthurdell/AYA/services/code_validator_service.py
echo "✅ Code validator executable"

# Create alias for easy access
SHELL_RC="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

# Add alias if not already present
if ! grep -q "alias validate-code" "$SHELL_RC" 2>/dev/null; then
    echo "">> "$SHELL_RC"
    echo "# AYA Code Validator" >> "$SHELL_RC"
    echo "alias validate-code='python3 /Users/arthurdell/AYA/services/code_validator_service.py'" >> "$SHELL_RC"
    echo "✅ Added shell alias: validate-code"
else
    echo "✅ Shell alias already exists"
fi

# Create validation wrapper for different nodes
cat > /Users/arthurdell/AYA/scripts/validate << 'WRAPPER_EOF'
#!/bin/bash
# AYA Code Validator Wrapper
# Automatically uses correct endpoint based on node

# Detect node and set appropriate flag
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"alpha"* ]] || [[ "$HOSTNAME" == *"ALPHA"* ]]; then
    # On ALPHA - use localhost
    EXTRA_FLAGS="--local"
else
    # On BETA, Gamma, AIR - use Tailscale
    EXTRA_FLAGS=""
fi

exec python3 /Users/arthurdell/AYA/services/code_validator_service.py $EXTRA_FLAGS "$@"
WRAPPER_EOF

chmod +x /Users/arthurdell/AYA/scripts/validate
echo "✅ Created smart wrapper: /Users/arthurdell/AYA/scripts/validate"

# Test the service
echo ""
echo "Testing code validator..."
if python3 /Users/arthurdell/AYA/services/code_validator_service.py test $([ "$USE_LOCAL" = true ] && echo "--local") > /dev/null 2>&1; then
    echo "✅ Code validator test passed"
else
    echo "⚠️  Code validator test had issues (check manually)"
fi

echo ""
echo "=== Setup Complete ===" 
echo ""
echo "Usage examples:"
echo ""
echo "  # Validate a single file"
echo "  validate validate --file mycode.py"
echo ""
echo "  # Validate multiple files"
echo "  validate batch --files file1.py file2.js file3.sh"
echo ""
echo "  # Validate code string"
echo "  validate validate --code 'def hello(): print(\"hi\")'"
echo ""
echo "  # Run test"
echo "  validate test"
echo ""
echo "  # Get statistics"
echo "  validate stats"
echo ""
echo "Or use the alias:"
echo "  validate-code test"
echo ""
echo "Configuration: /Users/arthurdell/AYA/config/code_validator_config.json"
echo "Service: /Users/arthurdell/AYA/services/code_validator_service.py"
echo ""

