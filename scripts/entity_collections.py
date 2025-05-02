from scripts.constants import *
from scripts.entities import Namespace, Secret, Node, Pod, Ingress, Job, StorageClass
from scripts.utils import KubectlCommand


class EntityCollection:
    def __init__(self, name, entity, namespace=None):
        self.name = name
        self.entity = entity
        self.namespace = namespace

    def get(self):
        cmd = KubectlCommand(command_part="{option} {name}".format(option=GET, name=self.name),
                             namespace=self.namespace)
        items = [self.entity(item_data) for item_data in cmd.run(output=JSON)["items"]]
        return items

    def exists(self, entity_name):
        cmd = KubectlCommand(
            "{option} {name} {entity_name}".format(option=GET, name=self.name, entity_name=entity_name),
            namespace=self.namespace)
        try:
            cmd.run(output=JSON)
        except:
            return False
        namespace = " in namespace %s" % cmd.namespace if cmd.namespace else ""
        print(("{entity} {name} already exists{namespace}.".format(entity=self.entity.__name__, name=entity_name,
                                                                   namespace=namespace)))
        return True


class Namespaces(EntityCollection):
    def __init__(self):
        EntityCollection.__init__(self, NAMESPACES, Namespace)


class Secrets(EntityCollection):
    def __init__(self, namespace):
        EntityCollection.__init__(self, name="secrets", entity=Secret, namespace=namespace)


class Nodes(EntityCollection):
    def __init__(self):
        EntityCollection.__init__(self, name="nodes", entity=Node)


class Pods(EntityCollection):
    def __init__(self, namespace):
        EntityCollection.__init__(self, name="pods", entity=Pod, namespace=namespace)


class Ingresses(EntityCollection):
    def __init__(self, namespace):
        EntityCollection.__init__(self, name="Ingresses", entity=Ingress, namespace=namespace)


class Jobs(EntityCollection):
    def __init__(self, namespace):
        EntityCollection.__init__(self, name="jobs", entity=Job, namespace=namespace)


class StorageClasses(EntityCollection):
    def __init__(self, namespace):
        EntityCollection.__init__(self, name="storageclasses", entity=StorageClass, namespace=namespace)
