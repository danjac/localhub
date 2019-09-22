# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig


class PrivateMessagesConfig(AppConfig):
    name = "localhub.private_messages"

    def ready(self):
        import localhub.private_messages.signals  # noqa
