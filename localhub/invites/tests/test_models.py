# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..factories import InviteFactory


pytestmark = pytest.mark.django_db


class TestInviteModel:
    def test_get_recipient_if_none(self):
        invite = InviteFactory(email="random@gmail.com")
        assert invite.get_recipient() is None

    def test_get_recipient_if_exists(self, user):
        invite = InviteFactory(email=user.email)
        assert invite.get_recipient() == user
