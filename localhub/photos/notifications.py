# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.activities.notifications import ActivityNotificationAdapter
from localhub.notifications import register

from .models import Photo


@register(Photo)
class PhotoNotificationAdapter(ActivityNotificationAdapter):
    ...
