from pytest import fixture
from retrying import retry

from scripts.constants import CURRENT_DIR
from scripts.entity_collections import Jobs
from scripts.tests.constants import CLUSTER_NAME
from scripts.tests.utils import get_rendered_template_file_name, apply_file_clean_at_the_end


def get_job_file():
    template_file = "vault-webhook-job.yaml.j2".format(current_dir=CURRENT_DIR)
    file_name = get_rendered_template_file_name(template_file, CLUSTER=CLUSTER_NAME)
    return file_name


@fixture
def create_job():
    job_file = get_job_file()
    yield from apply_file_clean_at_the_end(job_file)


class TestVaultWebHook:
    def test_secret_retrieved(self, create_job):
        self.check_job_finshed_with_success()

    @retry(retry_on_result=lambda is_success: not is_success, stop_max_delay=300000, wait_fixed=10000)
    def check_job_finshed_with_success(self):
        jobs = Jobs(namespace="default").get()
        return any(job.any_finished_job_with_success() for job in jobs if job.name() == "test-vault-job")