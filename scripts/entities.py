from dateutil import parser

from scripts.constants import *


class Entity():
    def __init__(self, data):
        self.data = data

    def name(self):
        return self.data.get(METADATA).get(NAME)


class Ingress(Entity):
    def hosts_records(self):
        return [rule["host"] for rule in self.data["spec"]["rules"]]

    def load_balancer_urls(self):
        return [ingress["hostname"] for ingress in self.data[STATUS]["loadBalancer"]["ingress"]]


class Namespace(Entity):
    pass


class Pod(Entity):
    def _ready_status(self):
        pod_status = self.data.get(STATUS)
        max_date = max([parser.parse(condition["lastTransitionTime"]) for condition in pod_status.get("conditions")])
        return next((condition.get(STATUS) for condition in pod_status.get("conditions") if
                     condition.get(TYPE) == "Ready" and
                     parser.parse(condition["lastTransitionTime"]) == max_date), False)

    def _all_container_ready_running(self):
        return all(
            container_status["ready"] and "running" in container_status["state"] for container_status in
            self._containers_statuses())

    def is_ok(self):
        return self._ready_status() and self._all_container_ready_running()

    def is_on_init_state(self):
        return any(containerStatus["state"]["waiting"]["reason"] == "PodInitializing" for containerStatus in
                   self.data.get(STATUS).get("containerStatuses") if self.data.get(STATUS)["phase"] == "Pending")

    def _containers_statuses(self): return [containerStatus for containerStatus in
                                            self.data.get(STATUS).get("containerStatuses")]


class Node(Entity):
    pass


class Secret(Entity):
    pass


class Job(Entity):
    def any_finished_job_with_success(self):
        return self.data["status"]["succeeded"] > 0 if "succeeded" in self.data["status"] else False

class StorageClass(Entity):
    pass
