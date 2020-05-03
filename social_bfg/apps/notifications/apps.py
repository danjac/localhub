# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "social_bfg.apps.notifications"

    def ready(self):
        self.module.autodiscover()
