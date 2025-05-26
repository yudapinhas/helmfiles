ROOT_DIR := $(shell pwd)
NAMESPACE_JENKINS := jenkins
NAMESPACE_ARGOCD := argocd
ENV := netgod-play-cluster

.PHONY: all netgod-deploy jenkins argocd port-forward-jenkins port-forward-argocd

all: netgod-deploy

netgod-deploy: ## Deploy Jenkins and ArgoCD via helmfile and expose services
	@echo "Syncing all Helm releases..."
	cd $(ROOT_DIR) && helmfile -e $(ENV) sync

	@echo "Ensuring Jenkins namespace exists..."
	kubectl create namespace $(NAMESPACE_JENKINS) --dry-run=client -o yaml | kubectl apply -f -

	@echo "Waiting for ArgoCD server to be ready..."
	kubectl wait --for=condition=available --timeout=120s deployment/argocd-server -n $(NAMESPACE_ARGOCD)

	@echo "Waiting for Jenkins to be ready..."
	kubectl wait --for=condition=available --timeout=120s deployment/jenkins -n $(NAMESPACE_JENKINS)

	@echo "ArgoCD available at https://localhost:8443"
	@echo "Jenkins available at http://localhost:8888"

	@echo "Starting port-forwards..."
	@echo "(CTRL+C to stop, or run in separate terminal)"
	@$(MAKE) port-forward-jenkins &
	@$(MAKE) port-forward-argocd &
	wait

port-forward-jenkins:
	nohup kubectl port-forward -n $(NAMESPACE_JENKINS) svc/jenkins 8888:8080 > /tmp/jenkins.log 2>&1 &

port-forward-argocd:
	nohup kubectl port-forward -n $(NAMESPACE_ARGOCD) svc/argocd-server 8443:443 > /tmp/argocd.log 2>&1 &