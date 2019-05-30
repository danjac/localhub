# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from communikit.core.types import ContextDict
from communikit.notifications.models import Notification

register = template.Library()


@register.simple_tag(takes_context=True)
def get_unread_notifications_count(context: ContextDict) -> int:

    request = context["request"]

    if request.user.is_anonymous:
        return 0
    return Notification.objects.filter(
        recipient=request.user,
        community=request.community,
        is_read=False,
    ).count()
