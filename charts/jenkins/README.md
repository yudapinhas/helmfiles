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

## 3️⃣ Secrets Configuration
The following values need to be provided and updated in `secrets.yaml`:
- `controller.ssh.privateKey` — Your GitHub SSH private key, **must be in RSA format**, used by Jenkins to pull repositories.
- `ngrok.authtoken` — Given for free after you create your ngrok account - https://dashboard.ngrok.com/
- `github-pat` - Github Personal Access Token (classic). Can be generated in Developer Settings for webhook intergration. Make sure it has the following permissions: repo, admin:repo_hook, admin:org_hook
- `terraform-cloud-token.token` - Free for use. Go to Terraform Cloud org settings --> Teams and generate team API token.
- `gcp.serviceAccountKey` - This is the credentials.json encoded in base64 format. The provider for actual resource creation.

## 4️⃣ Prepare repositories for CI/CD:
- The chart Retrieves Groovy DSL scripts from the repositories listed in the `repos.yaml` file.
  It expects each repository to follow this structure:
  ```
  buildScripts/jenkins/
      └── pipeline/
          ├── pull_request.groovy
      │   └── release.groovy
  ```

  You can take example from git@github.com:yudapinhas/netgod-terraform.git repository which we used for testing.
- Add your own repos to charts/jenkins/jenkins-dsl/repos.groovy.

## 5️⃣ Deployment Script
Run the Makefile `make netgod-deploy` to deploy Jenkins

---

# 🚀 How It Works

## 1️⃣ When Jenkins starts, JCasC provisions:
- System configuration
- Global credentials (including the github-ssh-key)
- A seed job called `seed-ci-cd-pipelines`

## 2️⃣ Generates CI/CD jobs
Runs the Job DSL to generate Jenkins jobs based on the pipeline Groovy scripts. For example, for the netgod-terraform repository, the following jobs are generated:
  - `netgod-terraform-pull-request` → builds and tests pull requests.
  - `netgod-terraform-release` → runs the release pipeline for production deployments.

## 3️⃣ jenkins-shared-lib
The generated jobs use the shared library `netgod-jenkins-shared-lib` to pull reusable Groovy steps and functions.

## 4️⃣ Webhooks automatic creation
To enable automatic CI/CD trigger flows, you just need to run the seed-ci-cd-pipelines job once, it will automatically intergrate the newly deployment of jenkins with your repositories including:
1. pullrequest job - Triggered by new pull requests and "retest this please" phrase inside a PR.
2. release job - Triggered first time automatically on latest merge. Triggered by merge to master.

These webhooks are created by using github-pat secret.

