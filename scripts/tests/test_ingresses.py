from pytest import fixture
from retrying import retry

from scripts.entity_collections import Jobs
from scripts.tests.constants import CLUSTER_NAME, CLUSTERS_DATA, CURRENT_CLUSTER_DATA
from scripts.tests.utils import ingresses, cluster_internal_zone_name, get_cluster_internal_records, \
    remove_last_dot_char, get_rendered_template_file_name, apply_file_clean_at_the_end
from scripts.utils import run_command
import json

def failed_ingress_exists(ingress_urls):
    return any(len(urls) == 0 for urls in ingress_urls)


def get_deployment_from_template_file(template_file):
    template_params = {"INTERNAL_DOMAIN": remove_last_dot_char(cluster_internal_zone_name()),
                       "CLUSTER": CLUSTER_NAME,
                       "ALB_INT": CURRENT_CLUSTER_DATA.get("ALB_INT", CLUSTERS_DATA['defaults']["ALB_INT"]),
                       "ALB_EXT": CURRENT_CLUSTER_DATA.get("ALB_EXT", CLUSTERS_DATA['defaults']["ALB_EXT"])
                       }
    return get_rendered_template_file_name(template_file, **template_params)


@fixture
def create_ingress():
    deployment_file = get_deployment_from_template_file("ingress-test.yaml.j2")
    yield from apply_file_clean_at_the_end(deployment_file)

@fixture
def create_alb_ingress():
    deployment_file = get_deployment_from_template_file("alb-ingress-test.yaml.j2")
    yield from apply_file_clean_at_the_end(deployment_file)

@fixture
def create_internal_test_job():
    deployment_file = get_deployment_from_template_file("test_apple_record_job.yaml.j2")
    yield from apply_file_clean_at_the_end(deployment_file, namespace="monitoring")


def retry_if_record_not_exists(record_exists):
    return not record_exists


class TestIngress:

    def test_all_ingress_elb_records_exists(self):
        self.check_ingress_url()

    def test_new_ingress_records_created(self, create_ingress, create_alb_ingress, create_internal_test_job):
        if "social" not in CLUSTER_NAME:
            self.check_external_record()
            if "ir" not in CLUSTER_NAME:
                self.check_internal_records_accessible_from_cluster()
                self.check_internal_record()

    @retry(retry_on_result=failed_ingress_exists, stop_max_delay=300000, wait_fixed=10000)
    def check_ingress_url(self):
        return [ingress.load_balancer_urls() for ingress in ingresses()]

    @retry(retry_on_result=retry_if_record_not_exists, stop_max_delay=300000, wait_fixed=10000)
    def check_internal_record(self):
        existing_records = get_cluster_internal_records()
        desired_records = [
            "apple-{cluster}.{domain}".format(domain=cluster_internal_zone_name(), cluster=CLUSTER_NAME),
            "apple-alb-{cluster}.{domain}".format(domain=cluster_internal_zone_name(), cluster=CLUSTER_NAME)
        ]
        return all(any(record == record_dict["Name"] for record_dict in existing_records) 
                  for record in desired_records)

    @retry(retry_on_result=retry_if_record_not_exists, stop_max_delay=300000, wait_fixed=10000)
    def check_external_record(self):
        records = [
            f"dig banana-{CLUSTER_NAME}.kenshoo.com @ns-1454.awsdns-53.org. +short | grep -E -o '([0-9]{{1,3}}[\.]){{3}}[0-9]{{1,3}}'",
            f"dig banana-alb-{CLUSTER_NAME}.kenshoo.com @ns-1454.awsdns-53.org. +short | grep -E -o '([0-9]{{1,3}}[\.]){{3}}[0-9]{{1,3}}'"
        ]
        results = [run_command(cmd) for cmd in records]
        return all(res.ok for res in results)

    @retry(retry_on_result=lambda record_exists: not record_exists, stop_max_delay=600000, wait_fixed=5000)
    def check_internal_records_accessible_from_cluster(self):
        return any([job.any_finished_job_with_success() for job in Jobs("monitoring").get() if
                    job.name() == "test-internal-ingress-record-job"])
