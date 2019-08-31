# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.conf import settings

from localhub.notifications.models import Notification

register = template.Library()


@register.inclusion_tag("notifications/includes/subscribe_btn.html")
def notifications_subscribe_btn(user, community):
    return {
        "user": user,
        "community": community,
        "vapid_public_key": settings.VAPID_PUBLIC_KEY,
    }


@register.simple_tag(takes_context=True)
def get_unread_notification_count(context, user, community):
    """
    Returns a cached count of the total number of *unread* notifications
    for the current user. If user not logged in just returns 0.
    """
    context_key = "_notifications_unread_count"
    if context_key in context:
        return context[context_key]
    if user.is_anonymous or not community.active:
        count = 0
    else:
        count = (
            Notification.objects.for_community(community)
            .filter(recipient=user, is_read=False)
            .count()
        )
    context[context_key] = count
    return count
