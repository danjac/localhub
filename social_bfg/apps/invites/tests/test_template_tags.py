# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

from ..templatetags.invites import get_pending_invite_count

pytestmark = pytest.mark.django_db


class TestPendingInviteCount:
    def test_pending_invite_count(self, invite, login_user):
        assert get_pending_invite_count(login_user) == 1
