# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django import template
from django.db.models import F
from django.urls import reverse

# Local
from ..models import Message

register = template.Library()


@register.inclusion_tag("private_messages/includes/message.html")
def render_message(
    request, user, message, conversation=None, is_detail=False, **extra_context
):
    """Renders a single message.

    Args:
        request (HttpRequest)
        user (User)
        message (Message)
        conversation (Message, optional): top level message (default: None)
        is_detail (bool, optional): if message is shown in detail view
        **extra_context: additional template variables

    Returns:
        dict: context dict
    """

    is_sender = user == message.sender
    is_recipient = user == message.recipient

    outbox_url = reverse("private_messages:outbox")
    sender_url = reverse("users:messages", args=[message.sender.username])
    recipient_url = reverse("users:messages", args=[message.recipient.username])

    can_send_message = user.has_perm(
        "private_messages.create_message", message.community
    )

    can_reply = can_send_message and is_recipient
    can_follow_up = can_send_message and is_sender

    message_url = message.get_absolute_url()

    parent = message.get_parent(user)

    if conversation and conversation == parent:
        parent = None

    parent_url = parent.get_absolute_url() if parent else None

    is_follow_up = parent and parent.sender == message.sender
    is_unread = is_recipient and not message.read

    return {
        "request": request,
        "user": user,
        "is_detail": is_detail,
        "is_recipient": is_recipient,
        "is_sender": is_sender,
        "is_unread": is_unread,
        "can_reply": can_reply,
        "can_follow_up": can_follow_up,
        "message": message,
        "message_url": message_url,
        "parent": parent,
        "parent_url": parent_url,
        "is_follow_up": is_follow_up,
        "recipient_url": recipient_url,
        "sender_url": sender_url,
        "other_user": message.get_other_user(user),
        "post_delete_redirect": outbox_url if is_detail else None,
        **extra_context,
    }


@register.simple_tag
def get_unread_message_count(user, community):
    """
    Returns a count of the total number of *unread* messages
    for the current user. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return (
        Message.objects.for_community(community)
        .for_recipient(user)
        .exclude_blocked(user)
        .unread()
        .filter(
            sender__membership__community=community,
            sender__membership__active=True,
            sender__is_active=True,
        )
        .count()
    )


@register.simple_tag
def get_unread_external_message_count(user, community):
    """
    Returns count of unread messages *outside* the current community,
    where the user is an active member. If user not logged in returns 0.
    """

    if user.is_anonymous or not community.active:
        return 0
    return (
        Message.objects.for_recipient(user)
        .exclude_blocked(user)
        .unread()
        .filter(
            community__membership__member=user,
            community__membership__active=True,
            community__active=True,
            sender__membership__community=F("community"),
            sender__membership__active=True,
            sender__is_active=True,
        )
        .exclude(community=community)
        .count()
    )
