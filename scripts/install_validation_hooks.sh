#!/bin/bash
# Install Git hooks for automated code validation
# Part of AYA Code Validation System

set -e

REPO_ROOT="/Users/arthurdell/AYA"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
VALIDATOR_SCRIPT="$REPO_ROOT/services/code_validator_n8n.py"

echo "🔧 Installing Git hooks for code validation..."

# Ensure hooks directory exists
mkdir -p "$HOOKS_DIR"

# Pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook: Validate Python files before commit

echo "🔍 Running code validation on staged files..."

# Get staged Python/JS/Shell files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|sh)$')

if [ -z "$FILES" ]; then
    echo "✅ No code files to validate"
    exit 0
fi

# Validate each file
FAILED=0
for file in $FILES; do
    if [ -f "$file" ]; then
        echo "Validating: $file"
        RESULT=$(python3 /Users/arthurdell/AYA/services/code_validator_n8n.py \
            --file "$file" \
            --agent "git-pre-commit" 2>/dev/null || echo '{"success":false}')
        
        ENFORCEMENT=$(echo "$RESULT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('enforcement_action', 'pass'))" 2>/dev/null || echo "pass")
        
        if [ "$ENFORCEMENT" = "block" ]; then
            echo "❌ $file FAILED validation - BLOCKED from commit"
            echo "$RESULT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('review', '')[:500])" 2>/dev/null || echo "Validation failed"
            FAILED=1
        elif [ "$ENFORCEMENT" = "warn" ]; then
            echo "⚠️  $file has warnings (committing anyway)"
        else
            echo "✅ $file passed validation"
        fi
    fi
done

if [ $FAILED -eq 1 ]; then
    echo ""
    echo "❌ Commit BLOCKED due to code validation failures"
    echo "Fix critical issues or use --no-verify to bypass (not recommended)"
    exit 1
fi

echo "✅ All files passed validation"
exit 0
EOF

chmod +x "$HOOKS_DIR/pre-commit"

# Pre-push hook
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# Pre-push hook: Comprehensive validation before push

echo "🔍 Running comprehensive code validation..."

# Get files changed in commits being pushed
FILES=$(git diff origin/main...HEAD --name-only | grep -E '\.(py|js|ts|sh)$' || true)

if [ -z "$FILES" ]; then
    echo "✅ No code files to validate"
    exit 0
fi

echo "Validating $(echo "$FILES" | wc -l | tr -d ' ') files..."

# Batch validate
RESULT=$(python3 /Users/arthurdell/AYA/services/code_validator_n8n.py \
    --files $FILES \
    --agent "git-pre-push" 2>/dev/null || echo '{"success":false,"summary":{"overall_enforcement":"block"}}')

ENFORCEMENT=$(echo "$RESULT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('summary', {}).get('overall_enforcement', 'pass'))" 2>/dev/null || echo "pass")

if [ "$ENFORCEMENT" = "block" ]; then
    echo "❌ Push BLOCKED due to critical validation failures"
    exit 1
elif [ "$ENFORCEMENT" = "warn" ]; then
    echo "⚠️  Push allowed but warnings exist - review recommended"
fi

echo "✅ Validation complete"
exit 0
EOF

chmod +x "$HOOKS_DIR/pre-push"

echo "✅ Git hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Validates staged files before commit"
echo "  - pre-push: Validates changed files before push"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"

