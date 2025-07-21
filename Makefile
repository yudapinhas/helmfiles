ROOT_DIR := $(shell pwd)
NAMESPACE_JENKINS := jenkins
NAMESPACE_ARGOCD := argocd
<<<<<<< HEAD
<<<<<<< HEAD
NAMESPACE_ARGOWORKFLOWS := argo-workflows
=======
NAMESPACE_MONITORING := monitoring
>>>>>>> a0cd23f (new/prometheus-grafana)
=======
NAMESPACE_MONITORING := monitoring
=======
NAMESPACE_ARGOWORKFLOWS := argo-workflows
>>>>>>> 3cc2f2a (fix kustomize workflows)
>>>>>>> f28c183 (rebase from master with monitoring)
ENV := netgod-play-cluster

.PHONY: all core-deploy jenkins argocd port-forward-jenkins port-forward-argocd

all: core-deploy

core-deploy: ## Deploy Jenkins and ArgoCD via helmfile and expose services
	@echo "Syncing all Helm releases..."
	cd $(ROOT_DIR) && helmfile -e $(ENV) -l group=core sync

	@echo "Ensuring Jenkins namespace exists..."
	kubectl create namespace $(NAMESPACE_JENKINS) --dry-run=client -o yaml | kubectl apply -f -

	@echo "Waiting for ArgoCD server to be ready..."
	kubectl wait --for=condition=available --timeout=120s deployment/argocd-server -n $(NAMESPACE_ARGOCD)

	@echo "Waiting for Jenkins to be ready..."
	kubectl wait --for=condition=available --timeout=120s deployment/jenkins -n $(NAMESPACE_JENKINS)

	@echo "ArgoCD available at https://localhost:8443"
	@echo "Jenkins available at http://localhost:8080"

	@echo "Starting port-forwards..."
	@echo "(CTRL+C to stop, or run in separate terminal)"
	@$(MAKE) port-forward-jenkins &
	@$(MAKE) port-forward-argocd &
	wait


argoworkflows-deploy: ## Deploy Jenkins and ArgoCD via helmfile and expose services
	@echo "Syncing all Helm releases..."
	cd $(ROOT_DIR) && helmfile -e $(ENV) -l group=argo-workflows sync

	@echo "Waiting for Argo Workflows to be ready..."
	kubectl wait --for=condition=available --timeout=120s deployment/argocd-server -n $(NAMESPACE_ARGOWORKFLOWS)

	@echo "Argo Workflows available at https://localhost:2746"

	@echo "Starting port-forwards..."
	@echo "(CTRL+C to stop, or run in separate terminal)"
	@$(MAKE) port-forward-argoworkflows &
	wait

.PHONY: destroy-all
destroy-all: ## Destroys all Helm releases across all groups
	@echo "Destroying all Helmfile-managed releases..."
	cd $(ROOT_DIR) && helmfile -e $(ENV) destroy

clean-namespaces:
	kubectl delete ns jenkins argocd argo-workflows || true

port-forward-jenkins:
	nohup kubectl port-forward -n $(NAMESPACE_JENKINS) svc/jenkins 8080:8080 > /tmp/jenkins.log 2>&1 &

port-forward-argocd:
	nohup kubectl port-forward -n $(NAMESPACE_ARGOCD) svc/argocd-server 8443:443 > /tmp/argocd.log 2>&1 &

port-forward-argoworkflows:
	nohup kubectl port-forward -n $(NAMESPACE_ARGOWORKFLOWS) svc/argo-workflows-server 2746:2746 > /tmp/argoworkflows.log 2>&1 &

port-forward-postgresql:
	nohup kubectl port-forward -n $(NAMESPACE_ARGOWORKFLOWS) svc/postgresql 2746:2746 > /tmp/postgresql.log 2>&1 &

port-forward-kafka: ### broker available at kafka.argo-workflows.svc.cluster.local:9092
	kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:4.0.0-debian-12-r7 --namespace $(NAMESPACE_ARGOWORKFLOWS) --command -- sleep infinity
port-forward-monitoring:
	nohup kubectl port-forward -n $(NAMESPACE_MONITORING) svc/kube-prometheus-stack-grafana 3000:80 > /tmp/kube-monitoring.log 2>&1 &
<<<<<<< HEAD
=======
	
port-forward-argoworkflows:
	nohup kubectl port-forward -n $(NAMESPACE_ARGOWORKFLOWS) svc/argo-workflows-server 2746:2746 > /tmp/argoworkflows.log 2>&1 &

port-forward-postgresql:
	nohup kubectl port-forward -n $(NAMESPACE_ARGOWORKFLOWS) svc/postgresql 2746:2746 > /tmp/postgresql.log 2>&1 &

port-forward-kafka: ### broker available at kafka.argo-workflows.svc.cluster.local:9092
	kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:4.0.0-debian-12-r7 --namespace $(NAMESPACE_ARGOWORKFLOWS) --command -- sleep infinity
>>>>>>> f28c183 (rebase from master with monitoring)
