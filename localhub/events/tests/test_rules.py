# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..factories import EventFactory

pytestmark = pytest.mark.django_db


class TestAttendPermissions:
    def test_is_member(self, member):
        event = EventFactory(community=member.community)
        assert member.member.has_perm("events.attend", event)

    def test_is_not_member(self, member):
        event = EventFactory()
        assert not member.member.has_perm("events.attend", event)

    def test_is_not_published(self, member):
        event = EventFactory(community=member.community, published=None)
        assert not member.member.has_perm("events.attend", event)
