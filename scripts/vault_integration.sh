#!/bin/bash
cluster_name=$1
vault_token=$2
vault_addr=$3

sudo yum install jq -y

if [ "$#" -ne 3 ]
then
  echo "One or more arguments are missing, please enter cluster name and vault token"
  exit 1
fi

export CLUSTER_NAME=$cluster_name
export SA_SECRET_NAME=$(kubectl get secrets -n kube-system --output=json | jq -r '.items[].metadata | select(.name=="vault-reviewer-token").name')
export REVIEWER_SA_JWT_TOKEN=$(kubectl get secret $SA_SECRET_NAME -n kube-system --output 'go-template={{ .data.token }}' | base64 --decode)
  
export KUBERNETES_CA_CERT=`./kubectl get cm kube-root-ca.crt -n kube-system -o jsonpath="{['data']['ca\.crt']}"`
export KUBERNETES_API_HOST=`./kubectl config view --minify -o jsonpath='{.clusters[*].cluster.server}'`

export ISSUER=`./kubectl get --raw /.well-known/openid-configuration | jq -r .issuer`

#Export Vault parameters
export VAULT_ADDR=$vault_addr
export VAULT_TOKEN=$vault_token

#Enable k8s plugin
./vault auth enable -path=kubernetes_${CLUSTER_NAME} kubernetes  2>/dev/null

#AUTH:
./vault write auth/kubernetes_${CLUSTER_NAME}/config \
  token_reviewer_jwt="${REVIEWER_SA_JWT_TOKEN}" \
  kubernetes_host="$KUBERNETES_API_HOST" \
  kubernetes_ca_cert="${KUBERNETES_CA_CERT}" \
  issuer=${ISSUER}

#POLICY:
./vault policy write sec_service_policy_kube_auth_${CLUSTER_NAME} -<<EOF
path "secret/kubernetes/kubernetes_${CLUSTER_NAME}/*" {
  capabilities = ["read", "list"]
}
EOF

#ROLE:
./vault write auth/kubernetes_${CLUSTER_NAME}/role/sec_service_role_kube_${CLUSTER_NAME} \
  bound_service_account_names=vault-approved \
  bound_service_account_namespaces='*' \
  policies=sec_service_policy_kube_auth_${CLUSTER_NAME} \
  ttl=1h
