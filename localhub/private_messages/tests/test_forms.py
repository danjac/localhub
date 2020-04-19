# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured

import pytest

from localhub.communities.factories import MembershipFactory
from localhub.users.factories import UserFactory

from ..forms import MessageForm

pytestmark = pytest.mark.django_db


class TestMessageForm:
    def test_clean_recipient_if_community_is_none(self, member):
        form = MessageForm(
            {"message": "test", "recipient": "@danjac"}, sender=member.member
        )
        with pytest.raises(ImproperlyConfigured):
            form.is_valid()

    def test_clean_recipient_if_sender_is_none(self, member):
        form = MessageForm(
            {"message": "test", "recipient": "@danjac"}, community=member.community
        )
        with pytest.raises(ImproperlyConfigured):
            form.is_valid()

    def test_clean_recipient_if_recipient_same_as_sender(self, member):
        form = MessageForm(
            {"message": "test", "recipient": f"@{member.member.username}"},
            community=member.community,
            sender=member.member,
        )
        assert not form.is_valid()

    def test_clean_recipient_if_recipient_blocked(self, member):
        user = MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        ).member
        member.member.blocked.add(user)
        form = MessageForm(
            {"message": "test", "recipient": "@danjac"},
            community=member.community,
            sender=member.member,
        )
        assert not form.is_valid()

    def test_clean_recipient_if_recipient_ok(self, member):
        user = MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        ).member
        form = MessageForm(
            {"message": "test", "recipient": "@danjac"},
            community=member.community,
            sender=member.member,
        )
        assert form.is_valid()
        assert form.cleaned_data["recipient"] == user

    def test_clean_if_no_recipient_field(self):
        form = MessageForm({"message": "test"})
        del form.fields["recipient"]
        assert form.is_valid()
