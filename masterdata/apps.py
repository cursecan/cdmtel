from django.apps import AppConfig


class MasterdataConfig(AppConfig):
    name = 'masterdata'

    def ready(self):
        from . import signals
