from django.apps import AppConfig


class PollsConfig(AppConfig):
    name = "localhub.polls"

    def ready(self):
        import localhub.polls.signals # noqa =
