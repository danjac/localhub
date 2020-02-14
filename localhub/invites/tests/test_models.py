# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..factories import InviteFactory
from ..models import Invite

pytestmark = pytest.mark.django_db


class TestInviteManager:
    def test_for_user(self, user):
        InviteFactory(email=user.email)
        assert Invite.objects.for_user(user).count() == 1


class TestInviteModel:
    def test_get_recipient_if_none(self):
        invite = InviteFactory(email="random@gmail.com")
        assert invite.get_recipient() is None

    def test_get_recipient_if_exists(self, user):
        invite = InviteFactory(email=user.email)
        assert invite.get_recipient() == user
