from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "communikit.events"

    def ready(self):
        import communikit.events.signals # noqa
