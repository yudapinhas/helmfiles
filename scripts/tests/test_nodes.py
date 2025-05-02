from retrying import retry

from scripts.utils import run_command


class TestNodes:

    def test_all_nodes_are_running(self):
        self.check_nodes()

    @retry(retry_on_result=lambda failed: failed, stop_max_delay=300000, wait_fixed=10000)
    def check_nodes(self):
        res = run_command("kubectl get nodes | grep -wv Ready")
        return not res.ok
