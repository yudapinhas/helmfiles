Why a Workflow and an Application?
Object	Kind	Lives in …	Purpose
kafka-to-sql-workflow.yaml	Workflow	kustomize/argo-pipelines	The thing that actually executes: jobs/steps/containers that read Kafka and write PostgreSQL.
kafka-to-sql-pipeline.yaml	Application	kustomize/argo-apps (or the Helm-rendered chart)	A pointer that tells Argo CD “watch that folder in Git (kustomize/argo-pipelines) and keep whatever is in there live in the cluster.”

Think of the Application CR as a GitOps subscription:
┌──────────────┐        watches/ syncs         ┌────────────────┐
│   Argo CD    │ ───────────────────────────▶ │ Workflow YAMLs │
└──────────────┘                              └────────────────┘
          ▲  Application CR
          └────────────────────────────── (kafka-to-sql-pipeline)

Workflow YAML – runtime recipe.

Application YAML – GitOps subscription.
Keeping them separate follows the app-of-apps pattern and gives you clean dashboards, safer promotion, and clearer ownership.