from django.apps import AppConfig


class MessagesConfig(AppConfig):
    name = "localhub.conversations"

    def ready(self):
        import localhub.conversations.signals  # noqa
