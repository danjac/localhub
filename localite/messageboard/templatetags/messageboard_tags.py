# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localite.core.types import ContextDict
from localite.messageboard.models import MessageRecipient

register = template.Library()


@register.simple_tag(takes_context=True)
def get_unread_messages_count(context: ContextDict) -> int:
    """
    Returns a count of the total number of *unread* messages
    for the current user. If user not logged in just returns 0.
    """

    request = context["request"]

    if request.user.is_anonymous:
        return 0
    return MessageRecipient.objects.filter(
        recipient=request.user,
        message__community=request.community,
        read__isnull=True,
    ).count()
