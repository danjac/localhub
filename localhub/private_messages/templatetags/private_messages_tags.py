# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.urls import reverse


register = template.Library()


@register.inclusion_tag(
    "private_messages/includes/message.html", takes_context=True
)
def show_message(
    context,
    user,
    message,
    show_sender_info=True,
    show_recipient_info=True,
    is_detail=False,
):

    is_sender = user == message.sender
    is_recipient = user == message.recipient
    outbox_url = reverse("private_messages:outbox")

    if is_sender:
        sender_url = outbox_url
        recipient_url = reverse(
            "users:messages", args=[message.recipient.username]
        )
        other_user = message.recipient
    else:
        sender_url = reverse("users:messages", args=[message.sender.username])
        recipient_url = outbox_url
        other_user = message.sender

    request = context["request"]

    can_create_message = request.user.has_perm(
        "private_messages.create_message", request.community
    )

    return {
        "request": request,
        "is_detail": is_detail,
        "is_recipient": is_recipient,
        "is_sender": is_sender,
        "message": message,
        "recipient_url": recipient_url,
        "sender_url": sender_url,
        "other_user": other_user,
        "show_recipient_info": show_recipient_info,
        "show_sender_info": show_sender_info,
        "can_create_message": can_create_message,
        "post_delete_redirect": outbox_url if is_detail else None,
    }


@register.simple_tag
def get_unread_message_count(user, community):
    """
    Returns a count of the total number of *unread* messages
    for the current user. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return user.get_unread_message_count(community)
