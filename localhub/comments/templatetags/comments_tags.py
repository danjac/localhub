# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

register = template.Library()


@register.inclusion_tag("comments/includes/comment.html")
def render_comment(request, user, comment, is_reply=False, **extra_context):
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
    content_object = comment.content_object

    if content_object and content_object.deleted:
        content_object = None

    show_content = not comment.deleted or comment.owner == user

    if is_reply or not getattr(comment, "is_parent_owner_member", True):
        parent = None
    else:
        parent = comment.parent

    if parent and parent.deleted:
        parent = None

    return {
        "request": request,
        "user": user,
        "comment": comment,
        "community": comment.community,
        "show_content": show_content,
        "content_object": content_object,
        "parent": parent,
        **extra_context,
    }
