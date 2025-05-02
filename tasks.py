import os

from invoke import task

from scripts.constants import CURRENT_DIR
from scripts.helm_utils import install_vault, install_helm, install_helm_diff, should_install_coredns_configmap_chart, \
    get_installed_helm_charts, run_helm_command
from scripts.helmfile_utils import install_helmfile, run_helmfile_command
from scripts.utils import is_coredns_configmap_exists, delete_existing_core_dns_configmap, \
    run_command, install_kubectl, run_check_external_dns_prefix, validate_yamls


@task()
def install_tools(ctx):
    install_vault()
    install_helm()
    install_helm_diff()
    install_helmfile()
    install_kubectl()


@task()
def validate_dns_configmap(ctx):
    if should_install_coredns_configmap_chart() and is_coredns_configmap_exists():
        delete_existing_core_dns_configmap()

@task(pre=[validate_dns_configmap])
def helmfile_init(ctx, cluster, vault_token, vault_addr):
    run_helmfile_command(cluster=cluster, command="-l name=kenshoo-namespace apply")
    run_helmfile_command(cluster=cluster, command="-l name=vault-integration apply")
    os.system("bash scripts/vault_integration.sh {cluster} {vault_token} {vault_addr}".format(cluster=cluster, vault_token=vault_token, vault_addr=vault_addr))

@task(pre=[validate_dns_configmap])
def helmfile_apply(ctx, cluster):
    run_helmfile_command(cluster=cluster, command="apply --concurrency 1")

@task
def helmfile_apply_chart(ctx, cluster, chart):
    run_helmfile_command(cluster=cluster, command="-l name={} apply".format(chart))

@task()
def helmfile_template(ctx, cluster):
    run_helmfile_command(cluster=cluster, command="template")


@task()
def helmfile_lint(ctx, cluster):
    run_helmfile_command(cluster=cluster, command="lint")


@task()
def helmfile_test(ctx, cluster):
    run_helmfile_command(cluster=cluster, command="-l testable=true test --cleanup")


@task
def test(ctx, cluster):
    run_command("pytest {current_dir}/scripts/tests/ -s --disable-warnings --verbose".format(
        current_dir=CURRENT_DIR), hide=None, env={**os.environ, **{"CLUSTER": cluster}})


@task()
def delete_all_charts(ctx):
    charts = get_installed_helm_charts()
    if len(charts):
      for chart in charts:
        if chart["name"] not in ["vault-integration", "kenshoo-namespace", "prometheus-operator" ]:
            run_helm_command("uninstall {release} -n {namespace}".format(release=chart["name"],namespace=chart["namespace"]))

@task()
def validation_tests(ctx, cluster):
    validate_yamls(cluster)
    run_check_external_dns_prefix(cluster=cluster)