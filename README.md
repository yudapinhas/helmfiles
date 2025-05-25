# 🚀 netgod-helmfiles

This repository is a Helmfile-based Kubernetes deployment playground designed for local testing and GitOps experimentation.  
It manages infrastructure like ArgoCD, Jenkins, and custom namespaces using declarative Helmfile workflows.

---

## 🧩 What’s inside

| Component         | Description                                      |
|-------------------|--------------------------------------------------|
| **Jenkins**       | Deployed via Helm chart to run CI/CD pipelines  |
| **ArgoCD**        | GitOps CD engine for Kubernetes                  |
| **Namespace Chart** | Declarative creation of `argocd`, `jenkins`, etc. |
| **Helmfile**      | Declarative orchestration of all components      |

---

## ▶️ Quick Start

Ensure you have `helmfile`, `kubectl`, and a running local Kubernetes cluster (like `minikube`).

1. Clone the repository
2. Deploy everything using:

```bash
make netgod-deploy