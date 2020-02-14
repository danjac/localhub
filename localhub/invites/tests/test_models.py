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
