from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = "localite.comments"

    def ready(self):
        import localite.comments.signals  # noqa
