from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = "communikit.comments"

    def ready(self):
        import communikit.comments.signals  # noqa
