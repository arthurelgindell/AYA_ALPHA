#!/bin/bash
# WEEK -14 DAY 1: COMPREHENSIVE VALIDATION SCRIPT
# Execute on: October 20, 2025
# Purpose: Validate all hardware, enforce air-gap, configure firewall
# Database: Log all results to gladiator_hardware_performance

set -e  # Exit on error

LOG_FILE="/Users/arthurdell/GLADIATOR/logs/week_-14_day_1_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /Users/arthurdell/GLADIATOR/logs

echo "========================================================================"
echo "WEEK -14 DAY 1: PHYSICAL SETUP & AIR-GAP ENFORCEMENT"
echo "Started: $(date)"
echo "========================================================================"
{

# =============================================================================
# TASK 1.1: ALPHA HARDWARE VALIDATION
# =============================================================================

echo -e "\n[TASK 1.1] ALPHA Hardware Validation"
echo "--------------------------------------------------------------------"

# Basic specs
HOSTNAME=$(hostname)
RAM_BYTES=$(sysctl -n hw.memsize)
RAM_GB=$((RAM_BYTES / 1024 / 1024 / 1024))
CPU_BRAND=$(sysctl -n machdep.cpu.brand_string)
PHYSICAL_CPU=$(sysctl -n hw.physicalcpu)
LOGICAL_CPU=$(sysctl -n hw.logicalcpu)

echo "Hostname: $HOSTNAME"
echo "RAM: ${RAM_GB} GB"
echo "CPU: $CPU_BRAND"
echo "Cores: $PHYSICAL_CPU physical, $LOGICAL_CPU logical"

# Verify RAM
if [ "$RAM_GB" -eq 512 ]; then
    echo "✅ RAM VERIFIED: 512 GB"
else
    echo "❌ RAM MISMATCH: Expected 512 GB, found ${RAM_GB} GB"
    exit 1
fi

# Storage
STORAGE_INFO=$(df -h / | tail -1)
echo "Storage: $STORAGE_INFO"

# =============================================================================
# TASK 1.2: BETA HARDWARE VALIDATION
# =============================================================================

echo -e "\n[TASK 1.2] BETA Hardware Validation"
echo "--------------------------------------------------------------------"

BETA_HOSTNAME=$(ssh beta.local "hostname")
BETA_RAM=$(ssh beta.local "sysctl -n hw.memsize | awk '{print \$1/1024/1024/1024}'")
BETA_STORAGE=$(ssh beta.local "df -h /Volumes/DATA | tail -1")

echo "Hostname: $BETA_HOSTNAME"
echo "RAM: ${BETA_RAM} GB"
echo "Storage: $BETA_STORAGE"

# Verify BETA RAM
if [ "${BETA_RAM%.*}" -eq 256 ]; then
    echo "✅ BETA RAM VERIFIED: 256 GB"
else
    echo "❌ BETA RAM MISMATCH: Expected 256 GB, found ${BETA_RAM} GB"
    exit 1
fi

# =============================================================================
# TASK 1.3: AIR-GAP ENFORCEMENT (CRITICAL)
# =============================================================================

echo -e "\n[TASK 1.3] Air-Gap Enforcement (CRITICAL)"
echo "--------------------------------------------------------------------"
echo "⚠️  POINT OF NO RETURN - Disconnecting from internet"
echo ""

# Disable Wi-Fi if present
echo "Disabling Wi-Fi on ALPHA..."
networksetup -setairportpower en0 off 2>/dev/null || echo "No Wi-Fi interface (OK)"

echo "Disabling Wi-Fi on BETA..."
ssh beta.local "networksetup -setairportpower en0 off" 2>/dev/null || echo "No Wi-Fi on BETA (OK)"

echo ""
echo "*** MANUAL ACTION REQUIRED ***"
echo "Physically disconnect WAN cable from network switch"
echo "Press ENTER when WAN cable is disconnected..."
read -r

# =============================================================================
# TASK 1.4: AIR-GAP VALIDATION (CRITICAL)
# =============================================================================

echo -e "\n[TASK 1.4] Air-Gap Validation"
echo "--------------------------------------------------------------------"

# Test external connectivity (MUST FAIL)
echo "Testing external connectivity (should FAIL)..."

EXTERNAL_TESTS=0
EXTERNAL_FAILED=0

echo -n "  ping 8.8.8.8: "
if ! ping -c 2 -W 2 8.8.8.8 >/dev/null 2>&1; then
    echo "❌ FAILED (correct - air-gapped)"
    EXTERNAL_FAILED=$((EXTERNAL_FAILED + 1))
else
    echo "✅ CONNECTED (WRONG - air-gap broken!)"
fi
EXTERNAL_TESTS=$((EXTERNAL_TESTS + 1))

echo -n "  ping 1.1.1.1: "
if ! ping -c 2 -W 2 1.1.1.1 >/dev/null 2>&1; then
    echo "❌ FAILED (correct - air-gapped)"
    EXTERNAL_FAILED=$((EXTERNAL_FAILED + 1))
else
    echo "✅ CONNECTED (WRONG - air-gap broken!)"
fi
EXTERNAL_TESTS=$((EXTERNAL_TESTS + 1))

echo -n "  curl google.com: "
if ! curl -m 3 https://google.com >/dev/null 2>&1; then
    echo "❌ FAILED (correct - air-gapped)"
    EXTERNAL_FAILED=$((EXTERNAL_FAILED + 1))
else
    echo "✅ CONNECTED (WRONG - air-gap broken!)"
fi
EXTERNAL_TESTS=$((EXTERNAL_TESTS + 1))

echo -n "  nslookup google.com: "
if ! nslookup google.com >/dev/null 2>&1; then
    echo "❌ FAILED (correct - air-gapped)"
    EXTERNAL_FAILED=$((EXTERNAL_FAILED + 1))
else
    echo "✅ CONNECTED (WRONG - air-gap broken!)"
fi
EXTERNAL_TESTS=$((EXTERNAL_TESTS + 1))

if [ "$EXTERNAL_FAILED" -eq "$EXTERNAL_TESTS" ]; then
    echo -e "\n✅ AIR-GAP VALIDATED: All external connectivity failed (correct)"
else
    echo -e "\n❌ AIR-GAP BROKEN: External connectivity still works!"
    exit 1
fi

# Test internal connectivity (MUST WORK)
echo -e "\nTesting internal connectivity (should WORK)..."

INTERNAL_TESTS=0
INTERNAL_PASSED=0

echo -n "  ping beta.local: "
if ping -c 3 beta.local >/dev/null 2>&1; then
    echo "✅ PASSED (correct)"
    INTERNAL_PASSED=$((INTERNAL_PASSED + 1))
else
    echo "❌ FAILED (WRONG - internal network broken!)"
fi
INTERNAL_TESTS=$((INTERNAL_TESTS + 1))

echo -n "  ssh beta.local: "
if ssh beta.local "echo ok" >/dev/null 2>&1; then
    echo "✅ PASSED (correct)"
    INTERNAL_PASSED=$((INTERNAL_PASSED + 1))
else
    echo "❌ FAILED (WRONG - SSH broken!)"
fi
INTERNAL_TESTS=$((INTERNAL_TESTS + 1))

if [ "$INTERNAL_PASSED" -eq "$INTERNAL_TESTS" ]; then
    echo -e "\n✅ INTERNAL NETWORK VALIDATED: All internal connectivity works"
else
    echo -e "\n❌ INTERNAL NETWORK BROKEN: Cannot communicate with BETA!"
    exit 1
fi

# =============================================================================
# TASK 1.5: LOG TO DATABASE
# =============================================================================

echo -e "\n[TASK 1.5] Logging to Database"
echo "--------------------------------------------------------------------"

psql -h localhost -U postgres -d aya_rag << 'SQLEOF'
-- Log air-gap validation
INSERT INTO gladiator_validation_tests (
    test_name, test_type, validation_gate, phase, tested_on,
    test_parameters, test_result, test_output,
    go_no_go_decision, decision_by
) VALUES (
    'Week -14 Day 1: Air-Gap Enforcement',
    'infrastructure',
    'gate_1',
    'phase_0',
    'ALPHA',
    '{"external_tests": 4, "internal_tests": 2}',
    'PASS',
    'External connectivity: 4/4 FAILED (correct). Internal connectivity: 2/2 PASSED (correct). Air-gap confirmed operational.',
    'GO',
    'cursor'
);

-- Update agent heartbeat
UPDATE gladiator_agent_coordination
SET last_heartbeat = NOW(),
    current_step = 'Air-gap validated',
    progress_percentage = 40
WHERE agent_id = 'cursor' AND status = 'working';

SQLEOF

echo "✅ Results logged to database"

echo -e "\n========================================================================"
echo "WEEK -14 DAY 1: VALIDATION COMPLETE"
echo "Completed: $(date)"
echo "========================================================================"

} | tee "$LOG_FILE"

echo -e "\nLog saved to: $LOG_FILE"
EOF
chmod +x /Users/arthurdell/GLADIATOR/scripts/week_14_day1_validation.sh
echo "✅ Week -14 Day 1 validation script created"
echo "Location: /Users/arthurdell/GLADIATOR/scripts/week_14_day1_validation.sh"
echo "Execute on: October 20, 2025"
