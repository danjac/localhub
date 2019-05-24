from django import template

from communikit.comments.models import CommentNotification
from communikit.posts.models import PostNotification
from communikit.types import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def get_unread_notifications_count(context: ContextDict) -> int:

    request = context["request"]

    if request.user.is_anonymous:
        return 0

    querysets = [
        model.objects.filter(
            recipient=request.user, community=request.community, is_read=False
        )
        for model in (CommentNotification, PostNotification)
    ]

    return querysets[0].union(*querysets[1:]).count()
