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

    def test_pending(self):
        InviteFactory(status=Invite.Status.PENDING)
        assert Invite.objects.pending().exists()

    def test_accepted(self):
        InviteFactory(status=Invite.Status.ACCEPTED)
        assert Invite.objects.accepted().exists()

    def test_rejected(self):
        InviteFactory(status=Invite.Status.REJECTED)
        assert Invite.objects.rejected().exists()

    def test_for_community(self, invite):
        assert Invite.objects.for_community(invite.community).exists()


class TestInvite:
    def test_is_pending(self):
        assert Invite(status=Invite.Status.PENDING).is_pending()

    def test_is_accepted(self):
        assert Invite(status=Invite.Status.ACCEPTED).is_accepted()

    def test_is_rejected(self):
        assert Invite(status=Invite.Status.REJECTED).is_rejected()
