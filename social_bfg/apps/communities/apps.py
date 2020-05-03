# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig


class CommunitiesConfig(AppConfig):
    name = "social_bfg.apps.communities"

    def ready(self):
        from . import signals  # noqa
