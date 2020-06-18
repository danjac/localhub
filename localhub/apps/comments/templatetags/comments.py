# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template

register = template.Library()


@register.inclusion_tag("comments/includes/comment.html")
def render_comment(
    request,
    user,
    comment,
    include_parent=True,
    include_content_object=True,
    **extra_context
):
    """Renders a single message.

    Args:
        request (HttpRequest)
        user (User)
        comment (Comment)
        is_reply (bool, optional): if comment is shown in list of replies
        **extra_context: additional template variables

    Returns:
        dict: context dict
    """
    show_content = not comment.deleted or comment.owner == user

    parent = comment.get_parent() if include_parent else None
    content_object = comment.get_content_object() if include_content_object else None

    return {
        "request": request,
        "user": user,
        "comment": comment,
        "community": comment.community,
        "show_content": show_content,
        "parent": parent,
        "content_object": content_object,
        "include_parent": include_parent,
        "include_content_object": include_content_object,
        **extra_context,
    }
