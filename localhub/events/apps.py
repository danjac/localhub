from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "localhub.events"

    def ready(self):
        from . import signals  # noqa
