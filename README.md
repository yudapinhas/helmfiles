# 🚀 netgod-helmfiles

This repository is a Helmfile-based Kubernetes deployment playground designed for local testing and GitOps experimentation.  
It manages infrastructure like ArgoCD, Jenkins, and custom namespaces using declarative Helmfile workflows.

---

## 🧩 What’s inside

| Component         | Description                                      |
|-------------------|--------------------------------------------------|
| **Jenkins**       | Deployed via Helm chart to run CI/CD for any repo|
| **ArgoCD**        | GitOps CD engine for Kubernetes                  |
| **ArgoApps**      | Template onboarding of new apps into ArgoCD      |
| **Namespace Chart** | Declarative creation of `argocd`, `jenkins`,etc|
| **Helmfile**      | Declarative orchestration of all components      |

---

## ▶️ Quick Start

Ensure you have `helmfile`, `kubectl`, and a running local Kubernetes cluster (like `minikube`).

1. Clone the repository
2. Deploy everything using:

```bash
make core-deploy
```

This will result with
- ArgoCD available at https://localhost:8443
- Jenkins available at http://localhost:8080 / ngrok public url in jenkins container logs.
- Argo-apps deployed and managed by argoCD - verify with ```kubectl get applications -n argocd``` 

## ▶ For ArgoWF and data etl pipelines run
```bash
make argoworkflows-deploy
```