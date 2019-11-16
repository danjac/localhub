# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.urls import reverse

from localhub.flags.models import Flag
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestFlagListView:
    def test_get(self, client, moderator):
        post = PostFactory(community=moderator.community)
        Flag.objects.create(
            content_object=post, community=moderator.community, user=UserFactory(),
        )
        response = client.get(reverse("flags:list"))
        assert response.status_code == 200


class TestFlagDeleteView:
    def test_post(self, client, moderator):
        post = PostFactory(community=moderator.community)
        flag = Flag.objects.create(
            content_object=post, community=moderator.community, user=UserFactory(),
        )
        response = client.post(reverse("flags:delete", args=[flag.id]))
        assert response.url == post.get_absolute_url()
        assert not Flag.objects.exists()
