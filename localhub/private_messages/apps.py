from django.apps import AppConfig


class PrivateMessagesConfig(AppConfig):
    name = "localhub.private_messages"

    def ready(self):
        import localhub.private_messages.signals  # noqa
