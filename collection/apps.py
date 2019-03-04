from django.apps import AppConfig


class CollectionConfig(AppConfig):
    name = 'collection'

    def ready(self):
        from . import signals