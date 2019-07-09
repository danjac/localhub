# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.test.client import Client
from django.urls import reverse

from taggit.models import Tag

from communikit.communities.models import Community, Membership
from communikit.events.tests.factories import EventFactory
from communikit.photos.tests.factories import PhotoFactory
from communikit.posts.tests.factories import PostFactory
from communikit.subscriptions.models import Subscription


pytestmark = pytest.mark.django_db


class TestActivityStreamView:
    def test_get_if_anonymous(self, client: Client, community: Community):
        PostFactory(community=community)
        EventFactory(community=community)

        response = client.get(reverse("activities:stream"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_if_authenticated_following(
        self, client: Client, member: Membership
    ):
        EventFactory(community=member.community)

        post = PostFactory(community=member.community)
        PostFactory(community=member.community, owner=member.member)

        Subscription.objects.create(
            subscriber=member.member,
            community=member.community,
            content_object=post.owner,
        )
        response = client.get(reverse("activities:stream"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_if_authenticated_show_all(
        self, client: Client, member: Membership
    ):
        EventFactory(community=member.community)
        post = PostFactory(community=member.community)
        PostFactory(community=member.community, owner=member.member)

        Subscription.objects.create(
            subscriber=member.member,
            community=member.community,
            content_object=post.owner,
        )
        response = client.get(reverse("activities:stream"), {"all": "1"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


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


class TestTagAutocompleteListView:
    def test_get(self, client: Client, community: Community):

        PostFactory(community=community).tags.add("movies")
        EventFactory(community=community).tags.add("movies")
        PhotoFactory(community=community).tags.add("movies")

        response = client.get(
            reverse("activities:tag_autocomplete_list"), {"q": "movie"}
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestTagSubscribeView:
    def test_post(self, client: Client, member: Membership):
        tag = Tag.objects.create(name="movies")
        response = client.post(
            reverse("activities:subscribe_tag", args=[tag.slug])
        )
        assert response.url == reverse("activities:tag", args=[tag.slug])
        sub = Subscription.objects.get()
        assert sub.content_object == tag
        assert sub.subscriber == member.member
        assert sub.community == member.community


class TestTagUnsubscribeView:
    def test_post(self, client: Client, member: Membership):
        tag = Tag.objects.create(name="movies")
        Subscription.objects.create(
            content_object=tag,
            subscriber=member.member,
            community=member.community,
        )
        response = client.post(
            reverse("activities:unsubscribe_tag", args=[tag.slug])
        )
        assert response.url == reverse("activities:tag", args=[tag.slug])
        assert not Subscription.objects.exists()
