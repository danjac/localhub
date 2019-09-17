# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.db.models import OuterRef
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
            .exclude(actor__in=user.blocked.all())
            .count()
        )
    context[context_key] = count
    return count


@register.simple_tag(takes_context=True)
def get_unread_local_network_notification_count(context, user, community):
    """
    Returns a cached count of the total number of *unread* notifications
    for the current user for all communities where user is member, excluding
    the current community. If user not logged in just returns 0.
    """
    context_key = "_notifications_unread_local_network_count"
    if context_key in context:
        return context[context_key]
    if user.is_anonymous or not community.active:
        count = 0
    else:
        count = (
            Notification.objects.filter(
                recipient=user,
                is_read=False,
                community__membership__member=user,
                community__membership__active=True,
                community__active=True,
                actor__membership__community=OuterRef("community"),
                actor__membership__active=True,
                actor__is_active=True,
            )
            .exclude(actor__in=user.blocked.all())
            .exclude(community=community)
            .count()
        )
    context[context_key] = count
    return count
