# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.apps.notifications.templatetags import notifications
from localhub.flags.templatetags import flags
from localhub.invites.templatetags import invites
from localhub.join_requests.templatetags import join_requests
from localhub.private_messages.templatetags import private_messages

from ..models import Community
from ..rules import is_admin, is_member, is_moderator

register = template.Library()


@register.simple_tag
def get_community_count(user):
    """
    Returns number of communities accessible to this user
    """
    if user.is_anonymous:
        return 0
    return Community.objects.accessible(user).count()


@register.simple_tag
def get_site_counters(user, community):
    """Returns dict of counters for:

    flags: Flags (moderators only)
    pending_join_requests: Pending join requests (admins only)
    sent_invites: Pending invites (admins only)
    messages: Unread messages
    notifications: Unread notifications
    total: Total of above

    Args:
        user (User): current user
        community (Community): current community

    Returns:
        dict
    """
    dct = {
        "flags": 0,
        "pending_join_requests": 0,
        "sent_invites": 0,
        "unread_messages": 0,
        "unread_notifications": 0,
        "total": 0,
    }

    if user.is_anonymous or not is_member(user, community):
        return dct

    dct.update(
        {
            "unread_messages": private_messages.get_unread_message_count(
                user, community
            ),
            "unread_notifications": notifications.get_unread_notification_count(
                user, community
            ),
        }
    )

    if is_moderator(user, community):
        dct.update({"flags": flags.get_flag_count(user, community)})

    if is_admin(user, community):
        dct.update(
            {
                "pending_join_requests": join_requests.get_pending_join_request_count(
                    user, community
                ),
            }
        )

    dct["total"] = sum(dct.values())
    return dct


@register.simple_tag
def get_external_site_counters(user, community):
    """Returns dict of counters for other sites for:

    flags: Flags (moderators only)
    pending_join_requests: Pending join requests (admins only)
    pending_invites: Pending invites to communities
    unread_messages: Unread messages
    unread_notifications: Unread notifications
    total: Total of above

    Args:
        user (User): current user
        community (Community): current community

    Returns:
        dict
    """
    dct = {
        "flags": 0,
        "pending_invites": 0,
        "pending_join_requests": 0,
        "unread_messages": 0,
        "unread_notifications": 0,
        "total": 0,
    }

    if user.is_anonymous:
        return dct

    dct.update(
        {
            "flags": flags.get_external_flag_count(user, community),
            "pending_join_requests": join_requests.get_pending_external_join_request_count(
                user, community
            ),
            "pending_invites": invites.get_pending_invite_count(user),
            "unread_messages": private_messages.get_unread_external_message_count(
                user, community
            ),
            "unread_notifications": notifications.get_unread_external_notification_count(
                user, community
            ),
        }
    )
    dct["total"] = sum(dct.values())
    return dct
