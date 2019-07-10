from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "localite.posts"

    def ready(self):
        import localite.posts.signals  # noqa
