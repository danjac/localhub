# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "localhub.events"

    def ready(self):
        from . import signals  # noqa
