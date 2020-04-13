# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse
from taggit.models import Tag

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.events.factories import EventFactory
from localhub.photos.factories import PhotoFactory
from localhub.posts.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestTagAutocompleteListView:
    def test_get(self, client, member):

        PostFactory(community=member.community, owner=member.member).tags.add("movies")
        EventFactory(community=member.community, owner=member.member).tags.add("movies")
        PhotoFactory(community=member.community, owner=member.member).tags.add("movies")

        response = client.get(reverse("hashtags:autocomplete_list"), {"q": "movie"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestTagFollowView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        response = client.post(reverse("hashtags:follow", args=[tag.id]))
        assert response.status_code == 200
        assert tag in member.member.following_tags.all()


class TestTagUnfollowView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        member.member.following_tags.add(tag)
        response = client.post(reverse("hashtags:unfollow", args=[tag.id]))
        assert response.status_code == 200
        assert tag not in member.member.following_tags.all()


class TestTagBlockView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        response = client.post(reverse("hashtags:block", args=[tag.id]))
        assert response.status_code == 200
        assert tag in member.member.blocked_tags.all()


class TestTagUnblockView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        member.member.blocked_tags.add(tag)
        response = client.post(reverse("hashtags:unblock", args=[tag.id]))
        assert response.status_code == 200
        assert tag not in member.member.blocked_tags.all()


class TestTagListView:
    def test_get(self, client, login_user):

        community = CommunityFactory(content_warning_tags="#nsfw #spoilers\n#aliens")
        member = MembershipFactory(community=community, member=login_user)

        PostFactory(community=member.community, owner=member.member).tags.add("movies")

        response = client.get(reverse("hashtags:list"), HTTP_HOST=community.domain)
        assert len(response.context["object_list"]) == 1
        assert response.context["content_warnings"] == ["nsfw", "spoilers", "aliens"]


class TestFollowingTagListView:
    def test_get(self, client, member):
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        ).tags.add("movies")
        member.member.following_tags.add(Tag.objects.get(name="movies"))

        response = client.get(reverse("hashtags:following_list"))
        assert len(response.context["object_list"]) == 1


class TestBlockedTagListView:
    def test_get(self, client, member):
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        ).tags.add("movies")
        member.member.blocked_tags.add(Tag.objects.get(name="movies"))

        response = client.get(reverse("hashtags:blocked_list"))
        assert len(response.context["object_list"]) == 1


class TestTagDetailView:
    def test_get(self, client, member):
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        ).tags.add("movies")
        response = client.get(reverse("hashtags:detail", args=["movies"]))
        assert response.context["tag"].name == "movies"
        assert len(response.context["object_list"]) == 1
