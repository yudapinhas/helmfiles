from pathlib import Path

KUBECTL_VERSION = 'v1.27.8'
HELM_VERSION = 'helm-v3.13.3'
VAULT_VERSION = '1.4.2'
VAULT_URL = 'https://releases.hashicorp.com/vault/{vault_version}/vault_{vault_version}_linux_amd64.zip'.format(
    vault_version=VAULT_VERSION)
HELM_URL = 'https://get.helm.sh/{helm_version}-linux-amd64.tar.gz'.format(helm_version=HELM_VERSION)
HELM_DIFF_PLUGIN = 'https://github.com/databus23/helm-diff'
HELM_DIFF_PLUGIN_VERSION = '3.6.0'
HELMFILE_VERSION = 'v0.140.0'
HELMFILE_INSTALLATION = 'https://github.com/roboll/helmfile/releases/download/{helmfile_version}/helmfile_linux_amd64'.format(
    helmfile_version=HELMFILE_VERSION)

CURRENT_DIR = Path(__file__).parent.parent
XDG_CONFIG_HOME = "%s/.helm/config" % CURRENT_DIR
XDG_CACHE_HOME = "%s/.helm/cache" % CURRENT_DIR
XDG_DATA_HOME = "%s/.helm/share" % CURRENT_DIR
HELM_V3_ENV = {"XDG_CONFIG_HOME": XDG_CONFIG_HOME, "XDG_CACHE_HOME": XDG_CACHE_HOME, "XDG_DATA_HOME": XDG_DATA_HOME}

LABELS = "labels"
METADATA = "metadata"
NODE = "node"
NAMESPACES = "namespaces"
NAME = "name"
GET = "get"
STATE = "state"
STATUS = "status"
ADDRESS = "address"
TYPE = "type"
KUBE_SYSTEM = "kube-system"
JSON = "json"
EXTERNAL_DNS_VALUES_FILE = ['external-dns-aws.yaml','external-dns-aws-shared-services.yaml']
