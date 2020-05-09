# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template
from django.conf import settings
from django.db.models import F

# Local
from ..models import Notification
from ..registry import registry

register = template.Library()


@register.tag(name="notification")
def render_notification(parser, token):
    """
    Renders notification object with the correct template.

    Example:
    {% notification notification %}
    <div class="notification">
        ...
        {{ notification_content }}
    </div>
    {% endnotification %}
    """
    try:
        _, notification = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Requires notification")

    nodelist = parser.parse(("endnotification",))
    parser.delete_first_token()

    return RenderNotificationNode(notification, nodelist)


class RenderNotificationNode(template.Node):
    def __init__(self, notification, nodelist):
        self.notification = template.Variable(notification)
        self.nodelist = nodelist

    def render(self, context):
        notification = self.notification.resolve(context)

        adapter = registry.get_adapter(notification)
        if adapter.is_allowed():
            context["notification_content"] = adapter.render_to_tag()
            content = self.nodelist.render(context)
            return content
        return ""


@register.inclusion_tag("notifications/includes/subscribe_btn.html")
def notifications_subscribe_btn(user, community):
    return {
        "user": user,
        "community": community,
        "vapid_public_key": settings.SOCIAL_BFG_VAPID_PUBLIC_KEY,
        "webpush_enabled": settings.SOCIAL_BFG_WEBPUSH_ENABLED,
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
