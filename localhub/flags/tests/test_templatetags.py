# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.posts.factories import PostFactory

# Local
from ..factories import FlagFactory
from ..templatetags.flags import get_external_flag_count, get_flag_count

pytestmark = pytest.mark.django_db


class TestGetFlagsCount:
    def test_get_count_if_moderator(self, moderator):
        post = PostFactory(community=moderator.community)
        FlagFactory(content_object=post, community=post.community)
        assert get_flag_count(moderator.member, moderator.community) == 1

    def test_get_count_if_not_moderator(self, member):
        post = PostFactory(community=member.community)
        FlagFactory(content_object=post, community=post.community)
        assert get_flag_count(member.member, member.community) == 0


class TestGetLocalNetworkFlagsCount:
    def test_get_count_if_moderator(self, moderator):
        post = PostFactory(community=moderator.community)
        FlagFactory(content_object=post, community=post.community)
        other = MembershipFactory(
            member=moderator.member, role=Membership.Role.MODERATOR
        )
        post = PostFactory(community=other.community)
        FlagFactory(content_object=post, community=post.community)
        assert get_external_flag_count(moderator.member, moderator.community) == 1

    def test_get_count_if_not_moderator(self, member):
        other = MembershipFactory(member=member.member)
        post = PostFactory(community=other.community)
        FlagFactory(
            content_object=post, community=post.community,
        )
        assert get_external_flag_count(member.member, member.community) == 0
