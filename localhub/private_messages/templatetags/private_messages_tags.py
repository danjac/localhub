# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


from localhub.communities.models import Community
from localhub.core.types import ContextDict
from localhub.private_messages.models import Message

register = template.Library()


@register.inclusion_tag("private_messages/includes/message.html")
def show_message(
    user: settings.AUTH_USER_MODEL,
    message: Message,
    show_sender_info: bool = True,
    show_recipient_info: bool = True,
    show_parent_info: bool = True,
    is_detail: bool = False,
) -> ContextDict:

    is_sender = user == message.sender
    is_recipient = user == message.recipient

    try:
        reply = message.reply
    except ObjectDoesNotExist:
        reply = None

    if is_sender:
        sender_url = reverse("private_messages:outbox")
        recipient_url = reverse(
            "users:messages", args=[message.recipient.username]
        )
        can_reply = False
    else:
        sender_url = reverse("users:messages", args=[message.sender.username])
        recipient_url = reverse("private_messages:outbox")
        can_reply = (
            reply is None
            and not message.sender_has_blocked
            and user.has_perm(
                "private_messages.create_message", message.community
            )
        )

    return {
        "can_reply": can_reply,
        "is_detail": is_detail,
        "is_recipient": is_recipient,
        "is_sender": is_sender,
        "message": message,
        "recipient_url": recipient_url,
        "reply": reply,
        "sender_url": sender_url,
        "show_recipient_info": show_recipient_info,
        "show_sender_info": show_sender_info,
        "show_parent_info": show_parent_info,
    }


@register.simple_tag
def get_unread_message_count(
    user: settings.AUTH_USER_MODEL, community: Community
) -> int:
    """
    Returns a count of the total number of *unread* messages
    for the current user. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return user.get_unread_message_count(community)
