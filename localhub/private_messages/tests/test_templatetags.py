# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from localhub.private_messages.templatetags.private_messages_tags import (
    get_unread_message_count,
    show_message,
)
from localhub.private_messages.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestShowMessage:
    def test_is_sender(self, req_factory, member):
        message = MessageFactory(
            sender=member.member, community=member.community
        )
        context = show_message(
            {"request": req_factory.get("/")}, member.member, message
        )
        assert context["sender_url"] == reverse("private_messages:outbox")
        assert context["recipient_url"] == reverse(
            "users:messages", args=[message.recipient.username]
        )

    def test_is_recipient(self, req_factory, member):
        message = MessageFactory(
            recipient=member.member, community=member.community
        )
        message.sender_has_blocked = False
        context = show_message(
            {"request": req_factory.get("/")}, member.member, message
        )
        assert context["recipient_url"] == reverse("private_messages:outbox")
        assert context["sender_url"] == reverse(
            "users:messages", args=[message.sender.username]
        )

    def test_is_recipient_sender_has_blocked(self, req_factory, member):
        message = MessageFactory(
            recipient=member.member, community=member.community
        )
        message.sender_has_blocked = True
        context = show_message(
            {"request": req_factory.get("/")}, member.member, message
        )
        assert context["recipient_url"] == reverse("private_messages:outbox")
        assert context["sender_url"] == reverse(
            "users:messages", args=[message.sender.username]
        )


class TestGetUnreadMessageCount:
    def test_anonymous(self, community):
        assert get_unread_message_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member):
        MessageFactory(community=member.community, recipient=member.member)
        assert get_unread_message_count(member.member, member.community) == 1
