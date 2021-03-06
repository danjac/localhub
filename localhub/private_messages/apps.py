# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PrivateMessagesConfig(AppConfig):
    name = "localhub.private_messages"
    verbose_name = _("Private Messages")

    def ready(self):
        from . import signals  # noqa
