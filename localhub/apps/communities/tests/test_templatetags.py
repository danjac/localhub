# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from localhub.apps.flags.factories import FlagFactory
from localhub.apps.join_requests.factories import JoinRequestFactory
from localhub.apps.private_messages.factories import MessageFactory
from localhub.invites.factories import InviteFactory

from ..factories import CommunityFactory, MembershipFactory
from ..models import Membership
from ..templatetags.communities import (
    get_community_count,
    get_external_site_counters,
    get_site_counters,
)

pytestmark = pytest.mark.django_db


class TestGetCommunityCount:
    def test_anonymous(self, community, anonymous_user):
        assert get_community_count(anonymous_user) == 0

    def test_authenticated(self, member):
        CommunityFactory(public=False)
        MembershipFactory(member=member.member).community
        assert get_community_count(member.member) == 2


class TestGetSiteCounters:
    def test_anonymous(self, community, anonymous_user):

        MessageFactory(community=community)
        JoinRequestFactory(community=community)
        FlagFactory(community=community)

        dct = get_site_counters(anonymous_user, community)

        assert dct["total"] == 0
        assert dct["unread_messages"] == 0
        assert dct["flags"] == 0
        assert dct["pending_join_requests"] == 0

    def test_member(self, community):

        member = MembershipFactory(community=community).member

        MessageFactory(
            community=community,
            recipient=member,
            sender=MembershipFactory(community=community).member,
        )
        JoinRequestFactory(community=community)
        FlagFactory(community=community)

        dct = get_site_counters(member, community)

        assert dct["total"] == 1
        assert dct["unread_messages"] == 1
        assert dct["flags"] == 0
        assert dct["pending_join_requests"] == 0

    def test_moderator(self, community):

        member = MembershipFactory(
            community=community, role=Membership.Role.MODERATOR
        ).member

        MessageFactory(
            community=community,
            recipient=member,
            sender=MembershipFactory(community=community).member,
        )
        JoinRequestFactory(community=community)
        FlagFactory(community=community)

        dct = get_site_counters(member, community)

        assert dct["total"] == 2
        assert dct["unread_messages"] == 1
        assert dct["flags"] == 1
        assert dct["pending_join_requests"] == 0

    def test_admin(self, community):
        member = MembershipFactory(
            community=community, role=Membership.Role.ADMIN
        ).member

        MessageFactory(
            community=community,
            recipient=member,
            sender=MembershipFactory(community=community).member,
        )
        JoinRequestFactory(community=community)
        FlagFactory(community=community)

        dct = get_site_counters(member, community)

        assert dct["total"] == 3
        assert dct["unread_messages"] == 1
        assert dct["flags"] == 1
        assert dct["pending_join_requests"] == 1


class TestGetExternalSiteCounters:
    def test_anonymous(self, community, anonymous_user):

        MessageFactory(community=community)
        JoinRequestFactory(community=community)
        FlagFactory(community=community)

        MessageFactory()
        JoinRequestFactory()
        FlagFactory()

        dct = get_external_site_counters(anonymous_user, community)

        assert dct["total"] == 0
        assert dct["unread_messages"] == 0
        assert dct["flags"] == 0
        assert dct["pending_invites"] == 0
        assert dct["pending_join_requests"] == 0

    def test_authenticated(self, community, anonymous_user):

        member = MembershipFactory(community=community,).member

        JoinRequestFactory()
        FlagFactory()

        MessageFactory(
            community=community,
            recipient=member,
            sender=MembershipFactory(community=community).member,
        )

        other = CommunityFactory()

        MembershipFactory(community=other, role=Membership.Role.ADMIN, member=member)

        MessageFactory(
            community=other,
            recipient=member,
            sender=MembershipFactory(community=other).member,
        )

        InviteFactory(email=member.email)

        dct = get_external_site_counters(anonymous_user, community)

        assert dct["total"] == 0
        assert dct["unread_messages"] == 0
        assert dct["flags"] == 0
        assert dct["pending_invites"] == 0
        assert dct["pending_join_requests"] == 0
