from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "communikit.events"

    def ready(self):
        from communikit.events import signals  # noqa
