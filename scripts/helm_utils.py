import urllib.request
from json import JSONDecodeError
from retry import retry

from scripts.constants import VAULT_URL, HELM_VERSION, HELM_URL, HELM_DIFF_PLUGIN, CURRENT_DIR, HELM_V3_ENV, HELM_DIFF_PLUGIN_VERSION
from scripts.utils import tarbal, moveToCurrentDirectory, unzip, make_executable, run_command

@retry(tries=3, delay=5)
def install_helm():
    try:
        print("Installing helm client...")
        print("Calling to URL: {url}".format(url=HELM_URL))
        urllib.request.urlretrieve(HELM_URL, '{filename}.tar.gz'.format(filename=HELM_VERSION))
        print("Tarbal the Helm.tar.gz file to current directory")
        tarbal('{filename}.tar.gz'.format(filename=HELM_VERSION))
        print("moving helm file to current directory")
        moveToCurrentDirectory('linux-amd64/helm')
        make_executable("helm")
    except Exception as e:
        raise Exception("Couldn't install helm client: ", e)

@retry(tries=3, delay=5)
def install_vault():
    try:
        print("installing Vault binary...")
        urllib.request.urlretrieve(VAULT_URL, 'vault')
        unzip("vault")
        make_executable("vault")
    except Exception as e:
        raise Exception("Couldn't install vault binary: ", e)

@retry(tries=3, delay=5)
def install_helm_diff():
    try:
        print("Check if helm-diff already exists")
        result = get_installed_helm_plugins()
        if ("diff" not in result) and (HELM_DIFF_PLUGIN_VERSION not in result):
            print("installing Diff plugin locally...")
            command = "{current_dir}/helm plugin install {helm_diff_plugin} --version {helm_diff_plugin_version}".format(
                helm_diff_plugin=HELM_DIFF_PLUGIN, current_dir=CURRENT_DIR, helm_diff_plugin_version=HELM_DIFF_PLUGIN_VERSION)
            run_command(command, env=HELM_V3_ENV)
    except Exception as e:
        raise Exception("Couldn't install helm diff plugin: ", e)

def should_install_coredns_configmap_chart():
    try:
        charts = get_installed_helm_charts()
        return all(chart["name"] != "coredns-config" for chart in charts)
    except JSONDecodeError:
        return False

def get_installed_helm_plugins():
    plugins = run_helm_command("plugin list")
    return plugins.stdout

def get_installed_helm_charts():
    charts = run_helm_command("ls --all-namespaces --output json --max 9999", load_json=True)
    return charts

def run_helm_command(cmd, **args):
    command = "{current_dir}/helm {cmd}".format(cmd=cmd, current_dir=CURRENT_DIR)
    return run_command(command, **args, env=HELM_V3_ENV)
