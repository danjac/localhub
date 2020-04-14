# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

import pytest

from django.utils import timezone

from ..factories import EventFactory

from ..rules import has_started

pytestmark = pytest.mark.django_db


class TestHasStarted:
    def test_has_not_started(self, user_model):
        event = EventFactory(starts=timezone.now() + timedelta(days=30))
        assert not has_started(user_model(), event)

    def test_has_started(self, user_model):
        event = EventFactory(starts=timezone.now() - timedelta(days=30))
        assert has_started(user_model(), event)


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

    def test_is_event_already_started(self, member):
        event = EventFactory(
            community=member.community, starts=timezone.now() - timedelta(days=30)
        )
        assert not member.member.has_perm("events.attend", event)
