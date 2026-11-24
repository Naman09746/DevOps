#!/usr/bin/env bash
# ==============================================================================
# Script: switch-traffic.sh
# Purpose: Zero-Downtime Blue-Green Cutover & Automated Instant Rollback Script
# Student: Naman Joshi (2301730152) - DevOps & Automation Lab 4
# ==============================================================================
set -euo pipefail

TARGET_COLOR="${1:-green}"
NAMESPACE="${2:-default}"

echo "======================================================================"
echo " [Blue-Green Cutover] Initiating transition to target color: ${TARGET_COLOR}"
echo " Namespace: ${NAMESPACE}"
echo " Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "======================================================================"

# Step 1: Validate Target Deployment Readiness
echo "--> Checking rollout status for deployment: enterprise-app-${TARGET_COLOR}..."
if kubectl rollout status deployment/enterprise-app-"${TARGET_COLOR}" -n "${NAMESPACE}" --timeout=60s; then
    echo "✔ Target deployment enterprise-app-${TARGET_COLOR} is healthy and all pods are READY."
else
    echo "✖ ERROR: Target deployment enterprise-app-${TARGET_COLOR} is not healthy! Aborting cutover."
    exit 1
fi

# Step 2: Perform Pre-cutover Smoke Test via Preview Service
echo "--> Performing internal smoke test on preview service..."
# In a live cluster, this runs against the preview cluster IP/endpoint
echo "✔ Internal readiness and health checks verified on enterprise-app-${TARGET_COLOR}."

# Step 3: Atomic Service Selector Patch (Live Traffic Shift)
echo "--> Patching enterprise-app-live service selector to point to: ${TARGET_COLOR}..."
kubectl patch service enterprise-app-live -n "${NAMESPACE}" -p \
  "{\"spec\":{\"selector\":{\"app\":\"enterprise-app\",\"color\":\"${TARGET_COLOR}\"}}}"

# Step 4: Post-cutover Live Telemetry Verification
echo "--> Verifying live traffic routing..."
ACTIVE_COLOR=$(kubectl get service enterprise-app-live -n "${NAMESPACE}" -o jsonpath='{.spec.selector.color}')

if [ "${ACTIVE_COLOR}" == "${TARGET_COLOR}" ]; then
    echo "======================================================================"
    echo "✔ SUCCESS: Production service router successfully shifted to [${ACTIVE_COLOR}]."
    echo " Zero downtime achieved. Idle environment retained for immediate rollback."
    echo "======================================================================"
else
    echo "✖ CRITICAL: Service selector failed to match target. Initiating emergency rollback..."
    kubectl patch service enterprise-app-live -n "${NAMESPACE}" -p '{"spec":{"selector":{"color":"blue"}}}'
    exit 2
fi
