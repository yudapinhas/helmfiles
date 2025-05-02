from _pytest.fixtures import fixture

from scripts.helm_utils import get_installed_helm_charts
from scripts.tests.constants import EXPECTED_CHARTS, NAMESPACES, CLUSTER_NAME


class TestHelmCharts:

    @fixture(scope="session", autouse=True)
    def charts(self):
        return [chart for chart in get_installed_helm_charts() if chart["namespace"] in NAMESPACES]

    @fixture(scope="session", autouse=True)
    def charts_names(self, charts):
        return set(chart["name"] for chart in charts)

    def test_all_charts_should_be_installed(self, charts_names):
        should_be_installed = EXPECTED_CHARTS.get(CLUSTER_NAME, EXPECTED_CHARTS.get('default')).difference(charts_names)
        assert len(should_be_installed) == 0, "The following charts are missing: {charts}".format(
            charts=",".join(should_be_installed))

    def test_only_expected_charts_are_installed(self, charts_names):
        should_not_be_installed = charts_names.difference(EXPECTED_CHARTS.get(CLUSTER_NAME, EXPECTED_CHARTS.get('default')))
        assert not should_not_be_installed, "The following charts are not expect to be installed: {charts}".format(
            charts=",".join(should_not_be_installed))

    def test_all_charts_in_status_deployed(self, charts):
        assert all(chart["status"] == "deployed" for chart in charts), f"The following charts are not in the 'deployed' status: {', '.join([chart['name'] for chart in charts if chart['status'] != 'deployed'])}"
