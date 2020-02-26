# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

from ..models import Flag
from ..templatetags.flags_tags import get_external_flag_count, get_flag_count

pytestmark = pytest.mark.django_db


class TestGetFlagsCount:
    def test_get_count_if_moderator(self, moderator):
        post = PostFactory(community=moderator.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        assert get_flag_count(moderator.member, moderator.community) == 1

    def test_get_count_if_not_moderator(self, member):
        post = PostFactory(community=member.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        assert get_flag_count(member.member, member.community) == 0


class TestGetLocalNetworkFlagsCount:
    def test_get_count_if_moderator(self, moderator):
        post = PostFactory(community=moderator.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        other = MembershipFactory(
            member=moderator.member, role=Membership.ROLES.moderator
        )
        post = PostFactory(community=other.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        assert get_external_flag_count(moderator.member, moderator.community) == 1

    def test_get_count_if_not_moderator(self, member):
        other = MembershipFactory(member=member.member)
        post = PostFactory(community=other.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        assert get_external_flag_count(member.member, member.community) == 0
