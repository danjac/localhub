# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.tests.factories import CommunityFactory
from localhub.users.tests.factories import UserFactory
from localhub.join_requests.forms import JoinRequestForm
from localhub.join_requests.tests.factories import JoinRequestFactory

pytestmark = pytest.mark.django_db


class TestJoinRequestForm:
    def test_sender_already_member(self, member):
        form = JoinRequestForm(member.community, member.member, {})
        assert not form.is_valid()

    def test_email_already_member(self, member):
        form = JoinRequestForm(
            member.community, None, {"email": member.member.email}
        )
        assert not form.is_valid()

    def test_if_join_request_exists_for_sender(self):
        sender = UserFactory()
        request = JoinRequestFactory(sender=sender)
        form = JoinRequestForm(request.community, sender, {})
        assert not form.is_valid()

    def test_if_join_request_exists_for_email(self):
        request = JoinRequestFactory(email="tester@gmail.com")
        form = JoinRequestForm(
            request.community, None, {"email": request.email}
        )
        assert not form.is_valid()

    def test_if_sender_email_in_blacklist(self):
        community = CommunityFactory(
            blacklisted_email_addresses="tester@gmail.com"
        )
        sender = UserFactory(email="tester@gmail.com")
        form = JoinRequestForm(community, sender, {})
        assert not form.is_valid()

    def test_email_in_blacklist(self):
        community = CommunityFactory(
            blacklisted_email_addresses="tester@gmail.com"
        )
        form = JoinRequestForm(community, None, {"email": "tester@gmail.com"})
        assert not form.is_valid()

    def test_email_ok(self):
        community = CommunityFactory()
        form = JoinRequestForm(community, None, {"email": "tester@gmail.com"})
        assert form.is_valid()

    def test_sender_ok(self):
        community = CommunityFactory()
        sender = UserFactory()
        form = JoinRequestForm(community, sender, {})
        assert form.is_valid()
