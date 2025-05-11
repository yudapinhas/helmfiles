# Jenkins Helm Chart — CI/CD Seed Job Setup

## Overview

This Helm chart deploys a Jenkins instance with a preconfigured seed job that automatically generates CI/CD pipelines for the netgod-terraform repository and related projects.

It is designed to bootstrap Jenkins jobs automatically using Job DSL and Jenkins Configuration as Code (JCasC), so you can spin up a ready-to-use Jenkins environment with minimal manual setup.

---

# 📦 What's Included

✅ Jenkins controller, deployed via Helm  
✅ Job DSL scripts mounted into the container  
✅ Seed job (seed-ci-cd-pipelines) that runs on startup to generate:
  - netgod-terraform-pull-request pipeline job
  - netgod-terraform-release pipeline job  
✅ Preconfigured SSH credentials for GitHub (github-ssh-key)  
✅ Linked shared pipeline library (netgod-jenkins-shared-lib) from GitHub

---

# 🔧 **Requirements**
## 1️⃣ Helm + Kubernetes Cluster
- Helm 3.x installed
- A running Kubernetes cluster (tested on Minikube, EKS, GKE, etc.)

## 2️⃣ Cloned Repositories Configuration
- Clone the helmfiles repositories:
```bash
git clone git@github.com:yudapinhas/helmfiles.git
git clone git@github.com:yudapinhas/jenkins-shared-lib.git
```

## 3️⃣ Values Configuration
The following values need to be provided and updated in `charts/jenkins/values.yaml`:
- `controller.ssh.privateKey` — Your GitHub SSH private key, **must be in RSA format**, used by Jenkins to pull repositories.
- `ngrok.authtoken` — Given for free after you create your ngrok account - https://dashboard.ngrok.com/

## 4️⃣ Deployment Script
Run the script `jenkins-shared-lib/scripts/deploy_jenkins.sh` to deploy Jenkins:

```bash
#!/bin/bash
set -e

NAMESPACE="jenkins"
ROOT_DIR=PATH/TO/CLONED/HELMFILES/HERE  # <--- EDIT TO YOUR PATH
cd "$ROOT_DIR"

echo "Creating/Updating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "Deploying Jenkins to namespace '$NAMESPACE'..."
helm upgrade --install jenkins ./charts/jenkins \
  -f ./charts/jenkins/values.yaml \
  -f ./values/netgod-play-cluster/netgod-jenkins.yaml \
  -n $NAMESPACE

echo "Jenkins deployment initiated. Run 'kubectl get pods -n $NAMESPACE' to check status."

kubectl port-forward -n jenkins svc/jenkins 8888:8080
echo "--- Jenkins pod is now exposed on port 8080 (127.0.0.1)"
```

---

# 🚀 How It Works

## 1️⃣ When Jenkins starts, JCasC provisions:
- System configuration
- Global credentials (including the github-ssh-key)
- A seed job called `seed-ci-cd-pipelines`

## 2️⃣ The seed job:
- Retrieves Groovy DSL scripts from the repositories listed in the `repos.yaml` file.
- Expects each repository to follow this structure:
  ```
  buildScripts/jenkins/
      ├── dsl/
      │   ├── pull_request.groovy
      │   └── release.groovy
      └── pipeline/
          ├── pull_request.groovy
          └── release.groovy
  ```
- Runs the Job DSL to generate Jenkins jobs based on the pipeline Groovy scripts. For example, for the netgod-terraform repository, the following jobs are generated:
  - `netgod-terraform-pull-request` → builds and tests pull requests.
  - `netgod-terraform-release` → runs the release pipeline for production deployments.

## 3️⃣ jenkins-shared-lib
The generated jobs use the shared library `netgod-jenkins-shared-lib` to pull reusable Groovy steps and functions.

## 4️⃣ Configure Webhooks
To enable automatic CI/CD trigger flows, you must configure GitHub webhooks for each repository that should notify Jenkins about events like pushes or pull requests.

These webhooks should point to your Jenkins server's public URL.

### 💻 Running Jenkins Locally?
If you're running Jenkins locally (e.g., using Minikube or Docker), you likely don't have a static public endpoint by default. To solve that, this Helm chart includes a sidecar container running ngrok, which automatically exposes your local Jenkins to the internet by generating a secure public URL.

The seed job will detect and print this URL when it runs, so you can easily grab and use it for webhook setup.

### ✅ Jenkins URL for Webhooks: https://e3a9-79-177-129-215.ngrok-free.app

### 🔁 How to Use It
Use the printed URL when configuring your GitHub webhooks. Append `/github-webhook/` to the end, like this:
```
https://e3a9-79-177-129-215.ngrok-free.app/github-webhook/
```

Repeat this for each repository you want Jenkins to listen to:

Set up the GitHub webhook in your repository:
- Go to Settings → Webhooks → Add webhook
- Payload URL → the ngrok URL + `/github-webhook/`
- Content type → application/json
- Events → choose "Just the push event" or "Let me select individual events," depending on what you want Jenkins to react to.