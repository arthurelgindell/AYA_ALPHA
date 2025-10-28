#!/bin/bash
# Diagnostic script for BETA Claude CLI authentication
# Run this on BETA to gather auth information

echo "═══════════════════════════════════════════════════════════════════"
echo "BETA CLAUDE CLI AUTHENTICATION DIAGNOSTIC"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

echo "[1/8] System Info"
echo "─────────────────────────────────────────────────────────────────"
echo "Hostname: $(hostname)"
echo "User: $(whoami)"
echo "Home: $HOME"
echo "PWD: $(pwd)"
echo ""

echo "[2/8] Claude CLI Location"
echo "─────────────────────────────────────────────────────────────────"
which claude
ls -la $(which claude) 2>/dev/null
file $(which claude) 2>/dev/null
echo ""

echo "[3/8] Claude Directories"
echo "─────────────────────────────────────────────────────────────────"
echo "~/.claude:"
ls -la ~/.claude 2>/dev/null || echo "  Does not exist"
echo ""
echo "~/.config/claude:"
ls -la ~/.config/claude 2>/dev/null || echo "  Does not exist"
echo ""
echo "~/Library/Application Support/Claude:"
ls -la ~/Library/Application\ Support/Claude 2>/dev/null | head -20 || echo "  Does not exist"
echo ""

echo "[4/8] Claude Desktop Process"
echo "─────────────────────────────────────────────────────────────────"
ps aux | grep -i claude | grep -v grep || echo "  No Claude processes found"
echo ""

echo "[5/8] Environment Variables"
echo "─────────────────────────────────────────────────────────────────"
env | grep -i claude || echo "  No Claude env vars"
env | grep -i anthropic || echo "  No Anthropic env vars"
echo ""

echo "[6/8] Keychain Check"
echo "─────────────────────────────────────────────────────────────────"
security find-generic-password -l "Claude" 2>&1 | grep -v "password:" || echo "  No Claude keychain entry"
security find-internet-password -s "claude.ai" 2>&1 | grep -v "password:" || echo "  No claude.ai keychain entry"
echo ""

echo "[7/8] Interactive Terminal Test"
echo "─────────────────────────────────────────────────────────────────"
echo "Testing: claude -p 'Echo: interactive test'"
timeout 30 claude -p "Echo: interactive test" 2>&1
echo "Exit code: $?"
echo ""

echo "[8/8] SSH Context Test"
echo "─────────────────────────────────────────────────────────────────"
echo "SSH_CONNECTION: ${SSH_CONNECTION:-not set}"
echo "SSH_CLIENT: ${SSH_CLIENT:-not set}"
echo "SSH_TTY: ${SSH_TTY:-not set}"
echo "TERM: ${TERM:-not set}"
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo "DIAGNOSTIC COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
