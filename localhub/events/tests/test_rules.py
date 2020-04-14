# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

import pytest
from django.utils import timezone

from ..factories import EventFactory
from ..rules import is_attendable

pytestmark = pytest.mark.django_db


class TestIsAttendable:
    def test_is_not_attendable(self, user_model):
        event = EventFactory(canceled=timezone.now())
        assert not is_attendable(user_model(), event)

    def test_is_attendable(self, user_model):
        event = EventFactory()
        assert is_attendable(user_model(), event)


class TestAttendPermissions:
    def test_is_member(self, member):
        event = EventFactory(community=member.community)
        assert member.member.has_perm("events.attend", event)

    def test_is_canceled(self, member):
        event = EventFactory(community=member.community, canceled=timezone.now())
        assert not member.member.has_perm("events.attend", event)

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


class TestCancelPermissions:
    def test_is_member(self, member):
        event = EventFactory(community=member.community)
        assert not member.member.has_perm("events.cancel", event)

    def test_is_owner(self, member):
        event = EventFactory(community=member.community, owner=member.member)
        assert member.member.has_perm("events.cancel", event)

    def test_is_moderator(self, moderator):
        event = EventFactory(community=moderator.community)
        assert moderator.member.has_perm("events.cancel", event)

    def test_is_canceled(self, member):
        event = EventFactory(
            community=member.community, canceled=timezone.now(), owner=member.member
        )
        assert not member.member.has_perm("events.cancel", event)

    def test_is_not_member(self, member):
        event = EventFactory()
        assert not member.member.has_perm("events.cancel", event)

    def test_is_not_published(self, member):
        event = EventFactory(
            community=member.community, published=None, owner=member.member
        )
        assert not member.member.has_perm("events.cancel", event)

    def test_is_event_already_started(self, member):
        event = EventFactory(
            community=member.community,
            starts=timezone.now() - timedelta(days=30),
            owner=member.member,
        )
        assert not member.member.has_perm("events.cancel", event)
