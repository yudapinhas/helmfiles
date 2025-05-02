from retrying import retry

from scripts.tests.utils import NAMESPACES
from scripts.entity_collections import Pods
from scripts.tests.utils import flatten_list
import re

def failed_pods_exists(pods):
    is_ignore_pods = re.compile(r"(test|prometheus|clean-evicted)")
    failed = [pod for pod in pods if not re.search(is_ignore_pods, pod)]
    return len(failed) > 0


class TestPods:

    def test_all_pods_are_running(self):
        self.check_pods()

    @retry(retry_on_result=failed_pods_exists, stop_max_delay=300000, wait_fixed=20000)
    def check_pods(self):
        pods = [Pods(ns).get() for ns in NAMESPACES]
        flat_pods = flatten_list(pods)
        not_ok = {pod.name() for pod in flat_pods if not pod.is_ok()}
        return not_ok
