from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    name = "localhub.conversations"

    def ready(self):
        import localhub.conversations.signals  # noqa
