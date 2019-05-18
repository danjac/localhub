from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = "communikit.posts"

    def ready(self):
        import communikit.posts.signals  # noqa
