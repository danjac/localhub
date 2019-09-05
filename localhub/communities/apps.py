from django.apps import AppConfig


class CommunitiesConfig(AppConfig):
    name = "localhub.communities"

    def ready(self):
        import localhub.communities.signals  # noqa
