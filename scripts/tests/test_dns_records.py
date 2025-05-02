from pytest import fixture
from retrying import retry
import re

from scripts.constants import CURRENT_DIR
from scripts.entity_collections import Jobs
from scripts.tests.utils import flatten_list, ingresses, get_cluster_internal_records, \
    remove_last_dot_char, apply_file_clean_at_the_end


def not_published_records_exists_pods_exists(records):
    return len(records) > 0


@fixture
def kenshoo_domain_job():
    deployment_file = "{current_dir}/scripts/tests/files/test_kenshoo_domains_job.yaml".format(
        current_dir=CURRENT_DIR)
    yield from apply_file_clean_at_the_end(deployment_file)

is_internal_records = re.compile(r".+\.(internalk(-lab|-stg)?.com|klocdev.info)").match

class TestAwsDnsRecords:
    def test_internal_records_exists(self):
        expected_records = self.get_ingress_expected_records()
        records_not_published = self.get_not_published_records(expected_records)
        assert len(records_not_published) == 0, \
            "These records were not published to internal hosted zone {records}".format(
                records=", ".join(records_not_published))

    def test_kenshoo_domains_are_accessible(self, kenshoo_domain_job):
        self.check_kenshoo_domain_accessible()

    @staticmethod
    def get_ingress_expected_records():
        return {record for ingress in ingresses() 
                  for record in ingress.hosts_records()
                    if is_internal_records(record)}

    @retry(retry_on_result=not_published_records_exists_pods_exists, stop_max_delay=300000, wait_fixed=10000)
    def get_not_published_records(self, expected_records):
        existing_records_names = set(
            [remove_last_dot_char(record["Name"]) for record in get_cluster_internal_records()])
        records_not_published = expected_records.difference(existing_records_names)
        return records_not_published

    @retry(retry_on_result=lambda record_exists: not record_exists, stop_max_delay=60000, wait_fixed=5000)
    def check_kenshoo_domain_accessible(self):
        return any([job.any_finished_job_with_success() for job in Jobs(namespace="default").get() if
                    job.name() == "test-kenshoo-domains-route"])
