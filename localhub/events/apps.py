from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "localhub.events"

    def ready(self):
        import localhub.events.signals  # noqa
