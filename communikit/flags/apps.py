from django.apps import AppConfig


class FlagsConfig(AppConfig):
    name = "communikit.flags"

    def ready(self):
        import communikit.flags.signals  # noqa
