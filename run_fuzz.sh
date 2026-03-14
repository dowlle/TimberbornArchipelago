#!/bin/bash
# Run all bananium-equivalent validation checks locally.
# Usage: bash run_fuzz.sh [multiplier]
#
# Default run counts match bananium: 5000 default, 5000 no-restrictive-starts, 500 rest.
# Pass a multiplier to scale (e.g. 0.1 for quick smoke test).

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AP_ROOT="$SCRIPT_DIR"

MULT="${1:-1}"

# Locate Python — prefer parent repo venv, fall back to system
if [[ -f "$SCRIPT_DIR/../.venv/Scripts/python.exe" ]]; then
    PYTHON="$SCRIPT_DIR/../.venv/Scripts/python.exe"
elif [[ -f "$SCRIPT_DIR/../.venv/bin/python" ]]; then
    PYTHON="$SCRIPT_DIR/../.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

cd "$AP_ROOT" || exit 1

FUZZ="fuzz.py"
GAME="timberborn"
JOBS=4
OUT_DIR="fuzz_output"
COMBINED_DIR="fuzz_results"

PASS=0
FAIL=0
STEP=0
TOTAL=10
RESULTS=""
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
START_TIME=$SECONDS

# Collect all failures in one place (fuzz.py wipes fuzz_output/ each run)
rm -rf "$COMBINED_DIR"
mkdir -p "$COMBINED_DIR"

run_check() {
    local name=$1
    local runs=$2
    shift 2
    STEP=$((STEP + 1))
    # Apply multiplier (minimum 1 run)
    runs=$("$PYTHON" -c "print(max(1, int($runs * $MULT)))" | tr -d '\r')
    echo "[$STEP/$TOTAL] === $name ($runs runs) ==="
    local check_start=$SECONDS
    # Pipe through cat so fuzz.py sees non-TTY and prints progress counts instead of dots
    if "$PYTHON" "$FUZZ" -j $JOBS -g $GAME -r $runs -n 1 "$@" 2>&1 | cat; then
        local elapsed=$(( SECONDS - check_start ))
        echo -e "[$STEP/$TOTAL] ${GREEN}PASS${NC}  $name  (${elapsed}s)"
        RESULTS="$RESULTS\n  ${GREEN}PASS${NC}  $name  (${elapsed}s)"
        PASS=$((PASS + 1))
    else
        local elapsed=$(( SECONDS - check_start ))
        echo -e "[$STEP/$TOTAL] ${RED}FAIL${NC}  $name  (${elapsed}s)"
        RESULTS="$RESULTS\n  ${RED}FAIL${NC}  $name  (${elapsed}s)"
        FAIL=$((FAIL + 1))
    fi
    # Preserve failures from this check before fuzz.py wipes them on next run
    if [ -d "$OUT_DIR/error" ]; then
        cp -r "$OUT_DIR/error" "$COMBINED_DIR/$name"
    fi
    echo ""
}

echo "Python: $PYTHON"
echo "AP root: $AP_ROOT"
echo "Running bananium validation suite for $GAME (multiplier=${MULT}x, $JOBS workers)"
echo "==========================================================================="
echo ""

run_check "default"                      5000
run_check "no-restrictive-starts"        5000  --hook hooks.no_rs:Hook
run_check "check-determinism"             500  --hook hooks.determinism:Hook
run_check "check-collect-accessibility"   500  --hook hooks.collect_accessibility_test:Hook
run_check "check-item-location-count"     500  --hook hooks.item_location_count:Hook
run_check "check-placement-refs"          500  --hook hooks.check_placement_item_location_references:Hook
run_check "check-lambda-capture"          500  --hook hooks.detect_rule_variable_capture_issues:Hook
run_check "check-static-output"           500  --hook hooks.detect_output_placement_changes:Hook
run_check "check-indirect-conditions"     500  --hook hooks.indirect_conditions:Hook
run_check "check-ut"                      500  --hook hooks.with_empty:Hook

TOTAL_TIME=$(( SECONDS - START_TIME ))
echo "==========================================================================="
echo "RESULTS: $PASS passed, $FAIL failed (total: ${TOTAL_TIME}s)"
echo -e "$RESULTS"
if [ $FAIL -gt 0 ]; then
    echo ""
    echo "Failure logs saved to $COMBINED_DIR/"
fi
echo ""

if [ $FAIL -gt 0 ]; then
    exit 1
fi
