#!/bin/bash
set -euo pipefail

#===============================================================================
# Local GitHub Actions Workflow Testing with nektos/act
#
# Usage:
#   ./test-workflow-locally.sh [workflow-file] [job-name]
#
# Examples:
#   ./test-workflow-locally.sh runner-smoke.yml
#   ./test-workflow-locally.sh runner-smoke.yml diagnostics-alpha
#===============================================================================

# Configuration
WORKFLOW_FILE="${1:-.github/workflows/runner-smoke.yml}"
JOB_NAME="${2:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}GitHub Actions Local Workflow Testing${NC}"
echo "=========================================="
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo -e "${RED}Error: 'act' is not installed${NC}"
    echo ""
    echo "Install with Homebrew:"
    echo "  brew install act"
    echo ""
    echo "Or download from: https://github.com/nektos/act"
    exit 1
fi

echo "✅ act is installed: $(act --version)"
echo ""

# Check if Docker is running (required by act)
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo ""
    echo "Start Docker Desktop or use colima:"
    echo "  colima start"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo -e "${RED}Error: Workflow file not found: $WORKFLOW_FILE${NC}"
    exit 1
fi

echo "📄 Workflow: $WORKFLOW_FILE"
[ -n "$JOB_NAME" ] && echo "🎯 Job: $JOB_NAME"
echo ""

# List available workflows if no specific job
if [ -z "$JOB_NAME" ]; then
    echo "Available jobs in workflow:"
    act -l -W "$WORKFLOW_FILE"
    echo ""
fi

# Run act
echo "🚀 Running workflow locally..."
echo "=========================================="

if [ -n "$JOB_NAME" ]; then
    # Run specific job
    act workflow_dispatch \
        -W "$WORKFLOW_FILE" \
        -j "$JOB_NAME" \
        --platform ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest \
        --platform macos-latest=sickcodes/docker-osx:latest \
        --verbose
else
    # Run all jobs
    act workflow_dispatch \
        -W "$WORKFLOW_FILE" \
        --platform ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest \
        --platform macos-latest=sickcodes/docker-osx:latest \
        --verbose
fi

echo ""
echo "=========================================="
echo "✅ Local workflow test complete"
echo ""
echo -e "${YELLOW}Note: act uses Docker containers which may not perfectly match${NC}"
echo -e "${YELLOW}the self-hosted macOS ARM64 environment. Always verify on actual runners.${NC}"
