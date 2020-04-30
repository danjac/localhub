# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured

import pytest

from localhub.apps.users.factories import UserFactory
from localhub.communities.factories import MembershipFactory

from ..forms import MessageRecipientForm

pytestmark = pytest.mark.django_db


class TestMessageRecipientForm:
    def test_clean_recipient_if_community_is_none(self, member):
        form = MessageRecipientForm(
            {"message": "test", "recipient": "@danjac"}, sender=member.member
        )
        with pytest.raises(ImproperlyConfigured):
            form.is_valid()

    def test_clean_recipient_if_sender_is_none(self, member):
        form = MessageRecipientForm(
            {"message": "test", "recipient": "@danjac"}, community=member.community
        )
        with pytest.raises(ImproperlyConfigured):
            form.is_valid()

    def test_clean_recipient_if_recipient_same_as_sender(self, member):
        form = MessageRecipientForm(
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
        form = MessageRecipientForm(
            {"message": "test", "recipient": "@danjac"},
            community=member.community,
            sender=member.member,
        )
        assert not form.is_valid()

    def test_clean_recipient_if_recipient_ok(self, member):
        user = MembershipFactory(
            member=UserFactory(username="danjac"), community=member.community
        ).member
        form = MessageRecipientForm(
            {"message": "test", "recipient": "@danjac"},
            community=member.community,
            sender=member.member,
        )
        assert form.is_valid()
        assert form.cleaned_data["recipient"] == user

    def test_clean_if_no_recipient_field(self):
        form = MessageRecipientForm({"message": "test"})
        del form.fields["recipient"]
        assert form.is_valid()
