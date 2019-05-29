# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from communikit.comments.models import CommentNotification
from communikit.events.models import EventNotification
from communikit.posts.models import PostNotification
from communikit.core.types import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def get_unread_notifications_count(context: ContextDict) -> int:

    request = context["request"]

    if request.user.is_anonymous:
        return 0

    querysets = [
        CommentNotification.objects.filter(
            recipient=request.user,
            comment__activity__community=request.community,
            is_read=False,
        ),
        EventNotification.objects.filter(
            recipient=request.user,
            event__community=request.community,
            is_read=False,
        ),
        PostNotification.objects.filter(
            recipient=request.user,
            post__community=request.community,
            is_read=False,
        ),
    ]

    return querysets[0].union(*querysets[1:]).count()
