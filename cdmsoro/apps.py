from django.apps import AppConfig


class CdmsoroConfig(AppConfig):
    name = 'cdmsoro'

    def ready(self):
        from . import signals