from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessageboardConfig(AppConfig):
    name = "localhub.messageboard"
    verbose_name = _("Message Board")
