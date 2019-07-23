# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.conf import settings


from localhub.communities.models import Community

register = template.Library()


@register.simple_tag
def get_unread_message_count(
    user: settings.AUTH_USER_MODEL, community: Community
) -> int:
    """
    Returns a count of the total number of *unread* messages
    for the current user. If user not logged in just returns 0.

    This value is cached in context.
    """

    if user.is_anonymous or community.is_anonymous:
        return 0
    return user.get_unread_message_count(community)
