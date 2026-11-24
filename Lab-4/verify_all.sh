#!/usr/bin/env bash
# ==============================================================================
# Master Verification Script for Lab 4 & Capstone Platform
# Student: Naman Joshi (2301730152) - DevOps & Automation Lab 4
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="${SCRIPT_DIR}"

cd "${BASE_DIR}"

echo "======================================================================"
echo " Starting Full Verification for Lab 4 & Capstone Platform"
echo " Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo " Workspace: ${BASE_DIR}"
echo "======================================================================"

# Make all scripts executable
chmod +x \
  verify_all.sh \
  k8s/blue-green/*.sh \
  k8s/canary/*.sh \
  disaster-recovery/*.sh \
  ci-cd/scripts/*.sh 2>/dev/null || true

# Step 1: Execute Automated Tests & Coverage
echo ""
echo ">>> [Phase 1/5] Running Automated Test Suite & Coverage <<<"
./ci-cd/scripts/test_runner.sh

# Step 2: DevSecOps SAST & Secret Leak Audit
echo ""
echo ">>> [Phase 2/5] Running DevSecOps Security Scan <<<"
./ci-cd/scripts/security_scan.sh

# Step 3: Kubernetes Kustomize Manifest Synthesis
echo ""
echo ">>> [Phase 3/5] Validating Kubernetes Manifests (Kustomize) <<<"
kubectl kustomize k8s/base/ > /dev/null
echo "✔ Kustomize base manifests compiled cleanly with zero syntax errors."

# Step 4: Disaster Recovery etcd Snapshot Verification
echo ""
echo ">>> [Phase 4/5] Running Disaster Recovery etcd Drill <<<"
./disaster-recovery/etcd-backup-restore.sh

# Step 5: Chaos Engineering Drill
echo ""
echo ">>> [Phase 5/5] Running Chaos Fault-Injection Drill <<<"
./disaster-recovery/chaos-resilience-test.sh

echo ""
echo "======================================================================"
echo "✔ ALL 5 PHASES VERIFIED SUCCESSFULLY!"
echo " The enterprise DevOps deployment toolkit and Capstone platform are ready."
echo "======================================================================"
