# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.users.factories import UserFactory
from localhub.posts.factories import PostFactory

from ..models import Flag
from ..templatetags.flags_tags import get_flags_count

pytestmark = pytest.mark.django_db


class TestGetFlagsCount:
    def test_get_count_if_moderator(self, moderator):
        post = PostFactory(community=moderator.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        assert get_flags_count(moderator.member, moderator.community) == 1

    def test_get_count_if_not_moderator(self, member):
        post = PostFactory(community=member.community)
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        assert get_flags_count(member.member, member.community) == 0
