# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.conf import settings

from localhub.communities.models import Community
from localhub.core.types import ContextDict

register = template.Library()


@register.inclusion_tag("notifications/includes/subscribe_btn.html")
def notifications_subscribe_btn(
    user: settings.AUTH_USER_MODEL, community: Community
) -> ContextDict:
    return {
        "user": user,
        "community": Community,
        "vapid_public_key": settings.VAPID_PUBLIC_KEY,
    }


@register.simple_tag
def get_unread_notification_count(
    user: settings.AUTH_USER_MODEL, community: Community
) -> int:
    """
    Returns a count of the total number of *unread* notifications
    for the current user. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return user.get_unread_notification_count(community)
