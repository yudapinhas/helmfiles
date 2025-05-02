import json
import os
import yaml
from retry import retry
from invoke import run
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
from scripts.constants import *


class KubectlCommand():
    def __init__(self, command_part, namespace=None):
        self.command_part = command_part
        self.namespace = namespace

    def run(self, output="", **args):
        cmd = self.build_command(output)
        load_json = output == JSON
        res = run_command(cmd, load_json=load_json, **args)
        return res

    def build_command(self, output):
        out_format = "--output=%s" % output if output else ""
        namespace_part = "--namespace=%s" % self.namespace if self.namespace else "--all-namespaces"
        return "{current_dir}/kubectl {part} {namespace} {output}".format(part=self.command_part,
                                                                          namespace=namespace_part,
                                                                          output=out_format, current_dir=CURRENT_DIR)

    @classmethod
    def run_file(cls, file, action="apply", namespace=None):
        return KubectlCommand("{action} -f {file}".format(file=file, action=action), namespace=namespace).run()


def make_executable(file):
    cmd = "chmod +x {current_dir}/{file}".format(current_dir=CURRENT_DIR, file=file)
    run_command(cmd)

def unzip(file):
    cmd = "unzip -o {current_dir}/{file}".format(current_dir=CURRENT_DIR, file=file)
    run_command(cmd)

def tarbal(file):
    cmd = "tar -zxvf {file}".format(file=file)
    run_command(cmd)

def moveToCurrentDirectory(fullPath):
    cmd = "mv {file} {current_dir}".format(file=fullPath, current_dir=CURRENT_DIR)
    run_command(cmd)

@retry(tries=3, delay=5)
def install_kubectl():
    try:
        print("Installing kubectl...")
        BASE_URL = "https://storage.googleapis.com/kubernetes-release/release"
        run(
            "curl -LO {kubectl_base_url}/{kubectl_version}/bin/linux/amd64/kubectl".format(
                kubectl_base_url=BASE_URL, kubectl_version=KUBECTL_VERSION))
        make_executable("kubectl")
    except Exception as e:
        raise Exception("Couldn't install kubectl: ", e)


def is_coredns_configmap_exists():
    res = KubectlCommand(command_part="get configMap coredns").run(warn=True)
    return res.ok


def delete_existing_core_dns_configmap():
    KubectlCommand("delete configMap coredns", namespace=KUBE_SYSTEM).run()


def run_command(cmd, hide='both', warn=False, load_json=False, env=None):
    res = run(cmd, hide=hide, warn=warn, env={**os.environ, **env} if env else os.environ)
    if load_json:
        return json.loads(res.stdout)
    return res


def build_kubectl_command(command):
    return "{current_dir}/kubectl {command}".format(current_dir=CURRENT_DIR, command=command)


def run_check_external_dns_prefix(cluster):
    for file in EXTERNAL_DNS_VALUES_FILE:
        fpath=f"values/{cluster}-cluster/{file}"
        with open(fpath) as f:
            dict = yaml.load(f, Loader=yaml.FullLoader)

            if dict:
                if dict['txtPrefix'] == cluster:
                    print(f"The txtPrefix:{dict['txtPrefix']} value equals the СlusterName:{cluster} on file:{file}")
                else:
                    raise NameError(f"txtPrefix:{dict['txtPrefix']} value does not equals ClusterName:{cluster} on file:{file}")

            elif not dict:
                if file == EXTERNAL_DNS_VALUES_FILE[1]:
                    print(f"The file {EXTERNAL_DNS_VALUES_FILE[1]} is Empty")
                elif file == EXTERNAL_DNS_VALUES_FILE[0]:
                    print(f"The file {EXTERNAL_DNS_VALUES_FILE[0]} is Empty")
                    raise NameError(f"The file {EXTERNAL_DNS_VALUES_FILE[0]} should not be empty")


def validate_yamls(cluster):
    yaml = YAML(typ='safe')
    values_path = f"{os.getcwd()}/values/{cluster}-cluster"
    for file in [os.path.join(values_path, item) for item in os.listdir(values_path)]:
        if file.endswith((".yaml", ".yml")):
            with open(file, "r") as stream:
                try:
                    print(f'Validating {file}')
                    yaml.load(stream)
                except DuplicateKeyError as e:
                    print(f"\033[91mCould not validate {file}\033[0m")
                    print(f"Duplicate key found in YAML file '{file}': {e}")
                    exit(12)
                except Exception as e:
                    print(f"\033[91mCould not validate {file}\033[0m")
                    print(f"Error in YAML file '{file}': {e}")
                    exit(12)