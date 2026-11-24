#!/usr/bin/env bash
# ==============================================================================
# Script: test_runner.sh
# Purpose: Comprehensive Automated Testing & Code Coverage Engine
# Student: Naman Joshi (2301730152) - DevOps & Automation Lab 4
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${BASE_DIR}"

echo "======================================================================"
echo " [CI/CD Automated Testing] Initializing Test Execution"
echo " Working Directory: $(pwd)"
echo " Python Runtime: $(python3 --version)"
echo "======================================================================"

mkdir -p reports

echo "--> Running Pytest with coverage reporting..."
python3 -m pytest -v \
  --cov=app \
  --cov-report=term \
  --cov-report=html:reports/coverage_html \
  --junitxml=reports/junit-results.xml \
  tests/

echo "======================================================================"
echo "✔ All tests passed successfully."
echo "  JUnit XML generated: reports/junit-results.xml"
echo "  Coverage Report generated: reports/coverage_html/index.html"
echo "======================================================================"
