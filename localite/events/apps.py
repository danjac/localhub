from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "localite.events"

    def ready(self):
        import localite.events.signals # noqa
