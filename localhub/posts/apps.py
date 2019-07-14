from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "localhub.posts"

    def ready(self):
        import localhub.posts.signals  # noqa
