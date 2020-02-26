# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.conf import settings
from django.db.models import F

from ..models import Notification

register = template.Library()


@register.inclusion_tag("notifications/includes/subscribe_btn.html")
def notifications_subscribe_btn(user, community):
    return {
        "user": user,
        "community": community,
        "vapid_public_key": settings.VAPID_PUBLIC_KEY,
    }


@register.simple_tag
def get_unread_notification_count(user, community):
    """
    Returns a count of the total number of *unread* notifications
    for the current user. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return (
        Notification.objects.for_community(community)
        .for_recipient(user)
        .exclude_blocked_actors(user)
        .unread()
        .count()
    )


@register.simple_tag
def get_unread_external_notification_count(user, community):
    """
    Returns a count of the total number of *unread* notifications
    for the current user for all communities where user is member, excluding
    the current community. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return (
        Notification.objects.filter(
            community__membership__member=user,
            community__membership__active=True,
            community__active=True,
            actor__membership__community=F("community"),
            actor__membership__active=True,
            actor__is_active=True,
        )
        .exclude(community=community)
        .for_recipient(user)
        .exclude_blocked_actors(user)
        .unread()
        .count()
    )
