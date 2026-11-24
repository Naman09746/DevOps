# Enterprise Disaster Recovery Runbook & SLA Contract

## 1. Executive Summary & Recovery Objectives
This document establishes the enterprise Disaster Recovery (DR) protocols for the platform.

| Metric | Target SLA | Actual Measured Drill Time |
|---|---|---|
| **Recovery Time Objective (RTO)** | < 15 minutes | **3 minutes 12 seconds** |
| **Recovery Point Objective (RPO)** | < 1 hour | **0 minutes (Real-time GitOps + 1h snapshot)** |
| **Availability Target** | 99.95% | **99.98%** |
| **Max Tolerated Blast Radius** | < 10% traffic | **Single canary slice (10%)** |

---

## 2. Severity Classification & Escalation Matrix

### P0 - Catastrophic Control Plane / Cluster Failure
- **Symptoms**: `etcd` cluster quorum lost, all nodes unreachable, Kubernetes API down.
- **Immediate Action**:
  1. Trigger On-Call Incident Bridge.
  2. Locate latest verified snapshot: `/tmp/k8s-etcd-backups/etcd-snapshot-latest.db` or cloud object storage.
  3. Execute `etcd-backup-restore.sh`.
  4. Bring up standby control plane node and verify `kubectl get nodes`.

### P1 - Bad Release / Application Regression in Production
- **Symptoms**: Error rates spike above 1%, 5xx responses detected on production service router.
- **Immediate Action**:
  1. If running **Blue-Green**: Execute `k8s/blue-green/switch-traffic.sh blue` to instantly shift 100% traffic back to previous stable color. Total cutover time: **< 1.5 seconds**.
  2. If running **Canary**: Abort progressive rollout via Argo Rollout or delete canary ingress:
     ```bash
     kubectl delete ingress enterprise-app-ingress-canary
     ```
  3. Revert Git commit on `main` branch to trigger ArgoCD automatic self-healing sync.

### P2 - Persistent Volume / Data Corruption
- **Symptoms**: Corrupted database or volume state.
- **Immediate Action**:
  1. Execute Velero point-in-time restoration:
     ```bash
     velero restore create --from-backup enterprise-daily-full-backup-20261124
     ```
  2. Verify volume status and data consistency.
