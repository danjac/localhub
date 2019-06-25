# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Membership
from communikit.flags.models import Flag
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestFlagListView:
    def test_get(self, client: Client, moderator: Membership):
        post = PostFactory(community=moderator.community)
        Flag.objects.create(
            content_object=post,
            community=moderator.community,
            user=UserFactory(),
        )
        response = client.get(reverse("flags:list"))
        assert response.status_code == 200


class TestFlagDeleteView:
    def test_delete(self, client: Client, moderator: Membership):
        post = PostFactory(community=moderator.community)
        flag = Flag.objects.create(
            content_object=post,
            community=moderator.community,
            user=UserFactory(),
        )
        response = client.delete(reverse("flags:delete", args=[flag.id]))
        assert response.url == post.get_absolute_url()
        assert not Flag.objects.exists()
