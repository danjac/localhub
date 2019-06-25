# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.activities.models import Like
from communikit.communities.models import Membership, Community
from communikit.events.tests.factories import EventFactory
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityProfileView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community, owner=member.member)
        EventFactory(community=member.community, owner=member.member)

        Like.objects.create(user=UserFactory(), activity=post)

        response = client.get(
            reverse("profile:activities", args=[member.member.username])
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2
        assert response.context["num_likes"] == 1


class TestActivityStreamView:
    def test_get(self, client: Client, community: Community):
        PostFactory(community=community)
        EventFactory(community=community)

        response = client.get(reverse("activities:stream"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2


class TestActivitySearchView:
    def test_get(self, client: Client, community: Community):
        post = PostFactory(community=community, title="test")
        event = EventFactory(community=community, title="test")

        for item in (post, event):
            item.make_search_updater()()

        response = client.get(reverse("activities:search"), {"q": "test"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_hashtag(self, client: Client, community: Community):
        post = PostFactory(community=community, description="#testme")
        post.make_search_updater()()
        response = client.get(reverse("activities:search"), {"q": "#testme"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1

    def test_get_if_search_string_empty(
        self, client: Client, community: Community
    ):

        response = client.get(reverse("activities:search"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0
