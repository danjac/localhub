# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest


from localhub.invites.forms import InviteForm
from localhub.invites.tests.factories import InviteFactory


pytestmark = pytest.mark.django_db


class TestInviteForm:
    def test_email_user_already_member(self, member):
        form = InviteForm(member.community, {"email": member.member.email})
        assert not form.is_valid()

    def test_email_already_sent(self):
        invite = InviteFactory()
        form = InviteForm(invite.community, {"email": invite.email})
        assert not form.is_valid()

    def test_email_ok(self, community):
        form = InviteForm(community, {"email": "tester@gmail.com"})
        assert form.is_valid()
