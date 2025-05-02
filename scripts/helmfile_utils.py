import urllib.request

from scripts.constants import HELMFILE_INSTALLATION, HELM_V3_ENV, CURRENT_DIR
from scripts.utils import make_executable, run_command
from retry import retry

@retry(tries=3, delay=5)
def install_helmfile():
    try:
        print("Installing helmfile...")
        urllib.request.urlretrieve(HELMFILE_INSTALLATION, 'helmfile')
        make_executable("helmfile")
    except Exception as e:
        raise Exception("Couldn't install helmfile: ", e)


def run_helmfile_command(cluster, command):
    helmfile_command = "{base_command} {specific_command}".format(base_command=_helmfile_base_command(cluster),
                                                                  specific_command=command)                                                            
    run_command(helmfile_command, env=HELM_V3_ENV)

def _helmfile_base_command(cluster):
    return "{current_dir}/helmfile -e {cluster}-cluster -b {current_dir}/helm".format(cluster=cluster,
                                                                                      current_dir=CURRENT_DIR)
