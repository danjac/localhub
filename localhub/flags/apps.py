from django.apps import AppConfig


class FlagsConfig(AppConfig):
    name = "localhub.flags"

    def ready(self):
        import localhub.flags.signals  # noqa
