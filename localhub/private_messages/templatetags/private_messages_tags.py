# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.db.models import F
from django.urls import reverse

from ..models import Message

register = template.Library()


@register.inclusion_tag("private_messages/includes/message.html", takes_context=True)
def show_message(
    context,
    user,
    message,
    show_sender_info=True,
    show_recipient_info=True,
    show_parent_info=True,
    is_detail=False,
    is_blocked=False,
):

    is_sender = user == message.sender
    is_recipient = user == message.recipient

    inbox_url = reverse("private_messages:inbox")
    outbox_url = reverse("private_messages:outbox")

    show_parent_info = (
        show_parent_info
        and message.parent
        and (is_recipient or (is_sender and not message.parent.is_hidden))
    )

    if is_sender:
        sender_url = outbox_url
        recipient_url = reverse("users:messages", args=[message.recipient.username])
    else:
        sender_url = reverse("users:messages", args=[message.sender.username])
        recipient_url = outbox_url

    request = context["request"]

    can_create_message = request.user.has_perm(
        "private_messages.create_message", request.community
    ) and not is_blocked

    return {
        "request": request,
        "is_detail": is_detail,
        "is_recipient": is_recipient,
        "is_sender": is_sender,
        "message": message,
        "recipient_url": recipient_url,
        "sender_url": sender_url,
        "other_user": message.get_other_user(user),
        "show_parent_info": show_parent_info,
        "show_recipient_info": show_recipient_info,
        "show_sender_info": show_sender_info,
        "can_create_message": can_create_message,
        "post_hide_redirect": inbox_url if is_detail else None,
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
    return (
        Message.objects.for_community(community)
        .for_recipient(user)
        .exclude_blocked_by_sender(user)
        .filter(
            read__isnull=True,
            sender__membership__community=community,
            sender__membership__active=True,
            sender__is_active=True,
        )
        .count()
    )


@register.simple_tag
def get_unread_local_network_message_count(user, community):
    """
    Returns count of unread messages *outside* the current community,
    where the user is an active member. If user not logged in returns 0.
    """

    if user.is_anonymous or not community.active:
        return 0
    return (
        Message.objects.for_recipient(user)
        .filter(
            read__isnull=True,
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
