# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from localhub.communities.models import Community, Membership
from localhub.private_messages.templatetags.private_messages_tags import (
    get_unread_message_count,
    show_message,
)
from localhub.private_messages.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestShowMessage:
    def test_is_sender(self, member: Membership):
        message = MessageFactory(
            sender=member.member, community=member.community
        )
        context = show_message(member.member, message)
        assert context["can_reply"] is False
        assert context["reply"] is None
        assert context["sender_url"] == reverse("private_messages:outbox")
        assert context["recipient_url"] == reverse(
            "users:messages", args=[message.recipient.username]
        )

    def test_is_recipient(self, member: Membership):
        message = MessageFactory(
            recipient=member.member, community=member.community
        )
        message.sender_has_blocked = False
        context = show_message(member.member, message)
        assert context["can_reply"] is True
        assert context["reply"] is None
        assert context["recipient_url"] == reverse("private_messages:outbox")
        assert context["sender_url"] == reverse(
            "users:messages", args=[message.sender.username]
        )

    def test_is_recipient_sender_has_blocked(self, member: Membership):
        message = MessageFactory(
            recipient=member.member, community=member.community
        )
        message.sender_has_blocked = True
        context = show_message(member.member, message)
        assert context["can_reply"] is False
        assert context["reply"] is None
        assert context["recipient_url"] == reverse("private_messages:outbox")
        assert context["sender_url"] == reverse(
            "users:messages", args=[message.sender.username]
        )

    def test_is_sender_has_reply(self, member: Membership):
        message = MessageFactory(
            sender=member.member, community=member.community
        )
        reply = MessageFactory(
            sender=message.recipient,
            community=message.community,
            recipient=message.sender,
            parent=message,
        )

        context = show_message(member.member, message)
        assert context["can_reply"] is False
        assert context["reply"] == reply
        assert context["sender_url"] == reverse("private_messages:outbox")
        assert context["recipient_url"] == reverse(
            "users:messages", args=[message.recipient.username]
        )

    def test_is_recipient_has_reply(self, member: Membership):
        message = MessageFactory(
            recipient=member.member, community=member.community
        )
        reply = MessageFactory(
            sender=message.recipient,
            community=message.community,
            recipient=message.sender,
            parent=message,
        )

        context = show_message(member.member, message)
        assert context["can_reply"] is False
        assert context["reply"] == reply
        assert context["recipient_url"] == reverse("private_messages:outbox")
        assert context["sender_url"] == reverse(
            "users:messages", args=[message.sender.username]
        )


class TestGetUnreadMessageCount:
    def test_anonymous(self, community: Community):
        assert get_unread_message_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member: Membership):
        MessageFactory(community=member.community, recipient=member.member)
        assert get_unread_message_count(member.member, member.community) == 1
