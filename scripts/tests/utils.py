import os
from functools import reduce
from tempfile import NamedTemporaryFile

from jinja2 import Template

from scripts.aws_utils import get_records_for_hosted_zone, get_hosted_zones
from scripts.constants import CURRENT_DIR
from scripts.entity_collections import Ingresses
from scripts.tests.constants import NAMESPACES, HOSTED_ZONE, CURRENT_CLUSTER_DATA
from scripts.utils import KubectlCommand


def flatten_list(list_of_lists):
    return reduce(lambda x, y: x + y, list_of_lists)


def ingresses():
    all_ingresses = [Ingresses(ns).get() for ns in NAMESPACES]
    flat_ingress = flatten_list(all_ingresses)
    return flat_ingress


def cluster_internal_zone_name():
    return CURRENT_CLUSTER_DATA[HOSTED_ZONE]


def get_hosted_zone_id():
    return next(zone["Id"] for zone in get_hosted_zones() if zone["Name"] == cluster_internal_zone_name())


def get_cluster_internal_records():
    zone_id = get_hosted_zone_id()
    return get_records_for_hosted_zone(zone_id)


def remove_last_dot_char(record):
    return record[:-1]


def get_rendered_template_file_name(template_file_name, **template_params):
    template_file = "{current_dir}/scripts/tests/template/{file_name}".format(current_dir=CURRENT_DIR,
                                                                              file_name=template_file_name)
    data = get_template_file_content(template_file, template_params)
    temp_file = write_to_temporary_file(data)
    return temp_file.name


def write_to_temporary_file(data):
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(data.encode('utf-8'))
        temp_file.close()
    return temp_file


def get_template_file_content(template_file, template_params):
    with open(template_file) as tmpl:
        data = Template(tmpl.read()).render(**template_params)
    return data


def apply_file_clean_at_the_end(file_name, namespace="default"):
    try:
        KubectlCommand.run_file(file_name, namespace=namespace)
        yield
        KubectlCommand.run_file(action="delete --force --grace-period 0", file=file_name, namespace=namespace)
    finally:
        os.path.exists(file_name)
