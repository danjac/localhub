# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.apps import AppConfig


class CommunitiesConfig(AppConfig):
    name = "localhub.communities"

    def ready(self):
        from . import signals  # noqa
