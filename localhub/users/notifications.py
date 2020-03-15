# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapter import BaseNotificationAdapter

from .utils import user_display


class UserNotificationAdapter(BaseNotificationAdapter):
    NOTIFICATION_HEADERS = {
        "new_follower": _("Someone has started following you"),
        "new_member": _("Someone has just joined this community"),
    }

    NOTIFICATION_BODY = {
        "new_follower": _("%(actor)s has started following you"),
        "new_member": _("%(actor)s has just joined this community"),
    }

    def get_notification_header(self):
        return dict(self.NOTIFICATION_HEADERS)[self.verb]

    def get_email_subject(self):
        return self.get_notification_header()

    def get_webpush_header(self):
        return self.get_notification_header()

    def get_webpush_body(self):
        return dict(self.NOTIFICATION_BODY)[self.verb] % {
            "actor": user_display(self.actor)
        }
