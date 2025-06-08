# 🚀 ArgoCD App-of-Apps — App Onboarding Guide

This repository implements the **App-of-Apps** pattern using ArgoCD to declaratively manage all microservices and platform components (like Jenkins, Grafana, Argo Workflows, etc.) for a given Kubernetes cluster.

Each **cluster** has its own **root `Application`**, which points to a **Kustomize overlay** located under `values/<cluster-name>/kustomization.yaml`. This enables **per-cluster customization** while reusing a shared base configuration.

---

## 📦 Repository Structure

```
helmfiles/
├── charts/
│   └── argo-apps/
│       └── templates/
│           └── root-app.yaml             # Root ArgoCD Application
├── kustomize/
│   └── argo-apps/
│       ├── base/
│       │   ├── jenkins.yaml              # ArgoCD Application for Jenkins
│       │   ├── anotherapp.yaml           # ArgoCD Application for other tools
│       │   └── kustomization.yaml        # Lists all base apps
├── values/
│   └── netgod-play-cluster/             # Example environment (overlay)
│       ├── kustomization.yaml           # Points to kustomize/argo-apps/base
│       └── argo-apps.yaml               # Values for the root-app
```

---

## ✨ Why Kustomize?

We use **Kustomize overlays** to enable per-cluster customization of the applications declared in the shared base.

This allows:
- Reusing the same app definitions (`jenkins.yaml`, etc.)
- Applying **environment-specific patches** (replicas, labels, annotations, etc.)
- Managing the whole environment declaratively via a single `kustomization.yaml` per cluster

For example, you can patch Jenkins to use 2 replicas in `netgod-play-cluster`, while keeping the base at 1.

---

## 🆕 How to Onboard a New Microservice or Platform Tool

### 1. Create a new ArgoCD `Application` manifest

Add a file under:  
`kustomize/argo-apps/base/my-service.yaml`

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: git@github.com:yudapinhas/helmfiles.git
    targetRevision: HEAD
    path: charts/my-service
    helm:
      valueFiles:
        - ../../values/netgod-play-cluster/my-service.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: my-service
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

### 2. Add the new app to the base `kustomization.yaml`

Edit `kustomize/argo-apps/base/kustomization.yaml`:

```yaml
resources:
  - jenkins.yaml
  - my-service.yaml   # ← Add your app here
```

---

### 3. Add environment-specific values (if needed)

If your chart uses values, add them under:

```
values/netgod-play-cluster/my-service.yaml
```

---

### 4. Sync via Helmfile

```bash
helmfile -e netgod-play-cluster sync
```

---

### 5. Verify in ArgoCD UI

```bash
kubectl get applications -n argocd
```

Or in the ArgoCD Web UI:

- Find the root app (e.g., `netgod-play-cluster`)
- Click **"Sync"**
- Enable **"Respect Ignore Differences"**
- Click **"Synchronize"**
- Your new service (`my-service`) should now appear

---
