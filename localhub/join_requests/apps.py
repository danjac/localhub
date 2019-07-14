from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JoinRequestsConfig(AppConfig):
    name = "localhub.join_requests"
    verbose_name = _("Join Requests")
