# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JoinRequestsConfig(AppConfig):
    name = "localhub.apps.join_requests"
    verbose_name = _("Join Requests")
