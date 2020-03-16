# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.activities.notifications import ActivityNotificationAdapter


class PollNotificationAdapter(ActivityNotificationAdapter):
    NOTIFICATION_HEADERS = ActivityNotificationAdapter.NOTIFICATION_HEADERS + [
        ("vote", _("%(actor)s has voted in your poll")),
    ]
