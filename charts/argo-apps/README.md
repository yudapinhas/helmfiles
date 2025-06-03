# ArgoCD App-of-Apps — Microservice Onboarding Guide

This chart manages the **root ArgoCD Application** for a given cluster using the App-of-Apps pattern.

Each cluster has its own root `Application` (e.g. `netgod-play-cluster`), which points to a `kustomization.yaml` file. That file defines all microservices (like Jenkins, Grafana, etc.) that should be managed for the cluster.

---

## ✅ Structure Overview
helmfiles/
├── charts/
│ └── argo-apps/ <--------- # This chart
    │ └── templates/
        │ └── root-app.yaml # ArgoCD Application baseline
├── kustomize/
│ └── argo-apps/
    │ └── base/
        │ ├── jenkins.yaml # ArgoCD App for Jenkins
        │ ├── grafana.yaml # ArgoCD App for Grafana
        │ └── kustomization.yaml # lists the above
├── values/
│ └── netgod-play-cluster/
│ ├── kustomization.yaml # points to kustomize/argo-apps/base
│ └── argo-apps.yaml # values for the root app

## 🆕 How to Onboard a New Microservice

1. **Create a new ArgoCD `Application` YAML for your service:**

Example: `kustomize/argo-apps/base/my-service.yaml`

```
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
  destination:
    server: https://kubernetes.default.svc
    namespace: my-service
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

2. **Add it to the base kustomization.yaml:**
File: kustomize/argo-apps/base/kustomization.yaml

```
resources:
  - jenkins.yaml
  - my-service.yaml  # ← Add your new file here
  ```

3. **Add it to the base kustomization.yaml:**
If your Helm chart uses values, place them under:
```values/netgod-play-cluster/my-service.yaml```

4. **Add it to the base kustomization.yaml:**
```helmfile -e netgod-play-cluster sync```

5. **Verify it's working:**
```kubectl get applications -n argocd```

- You should now see my-service listed and synced.
- Warning! I do not recommend to refresh an argo-app from UI will cause sync between helmfiles repo into your live cluster - it will erase the secrets values