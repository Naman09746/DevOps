# GitOps Architecture & Repository Layout

## 1. Declarative Source of Truth Principle
In this enterprise DevOps platform, **Git is the single source of truth** for all desired state configurations. Direct `kubectl apply` commands against production clusters are strictly prohibited. Every infrastructure alteration, secret reference update, or container image bump must be committed through Git with signed commits and automated CI validation.

```
       Developer Commit / PR
                 │
                 ▼
       GitHub Actions / Jenkins (CI)
    (Test, Lint, SAST, Multi-stage Build)
                 │
                 ▼
       Push Image to Registry (ghcr.io)
                 │
                 ▼
       Automated GitOps Manifest Update
                 │
                 ▼
       ArgoCD Reconciliation Loop (Pull-Based CD)
       (Continuous Drift Detection & Self-Healing)
                 │
                 ▼
       Kubernetes Production Cluster
    (Blue-Green / Canary Traffic Routing)
```

## 2. Push-Based vs. Pull-Based CD Trade-Offs

| Evaluation Metric | Push-Based Deployment (Jenkins/GitHub Runner) | Pull-Based GitOps (ArgoCD / Flux) |
|---|---|---|
| **Cluster Access Security** | CI server requires admin `kubeconfig` with write privileges | Cluster pulls inwards; **no external cluster credentials exposed** |
| **Drift Detection** | None (cluster can diverge unnoticed) | **Continuous active reconciliation** against Git every 60s |
| **Self-Healing** | Requires manual or scheduled redeployment | **Automatic reversal** of manual out-of-band cluster edits |
| **Auditability & Compliance** | Audit trail split across CI runner logs and audit sinks | **Full cryptographic Git commit log** acts as audit trail |
| **Disaster Recovery** | Manual script execution required | **Instant cluster restoration** by pointing ArgoCD to Git |

## 3. Directory Layout Rationale
- `k8s/base/`: Contains clean Kustomize-managed canonical manifests (Deployment, Service, ConfigMap, HPA).
- `k8s/blue-green/`: Dedicated zero-downtime Blue/Green manifests and cutover scripts.
- `k8s/canary/`: Nginx Ingress / Argo Rollouts canary traffic splitting definitions.
- `k8s/secrets/`: Vault Agent Injector annotations and RBAC bindings.
