from scripts.entity_collections import StorageClasses
from scripts.tests.constants import STORAGE_CLASSES

class TestStorageClass:
    def test_storage_class_exists(self):
        storage_classes = StorageClasses(namespace=None).get()

        assert any(sc.name() in STORAGE_CLASSES for sc in storage_classes)
