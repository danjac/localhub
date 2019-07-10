from django.apps import AppConfig


class FlagsConfig(AppConfig):
    name = "localite.flags"

    def ready(self):
        import localite.flags.signals  # noqa
