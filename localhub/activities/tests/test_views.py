# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse
from taggit.models import Tag

from localhub.communities.factories import MembershipFactory
from localhub.events.factories import EventFactory
from localhub.photos.factories import PhotoFactory
from localhub.polls.factories import AnswerFactory, PollFactory
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityStreamView:
    def test_get_if_anonymous(self, client, community):
        response = client.get(reverse("activities:stream"))
        assert response.url == reverse("community_welcome")

    def test_get_if_non_member(self, client, login_user, community):
        response = client.get(reverse("activities:stream"))
        assert response.url == reverse("community_welcome")

    def test_get_if_member(self, client, member):
        EventFactory(community=member.community, owner=member.member)
        PostFactory(community=member.community, owner=member.member)
        PostFactory(community=member.community, owner=member.member)
        poll = PollFactory(community=member.community, owner=member.member)

        for _ in range(3):
            answer = AnswerFactory(poll=poll)
            answer.voters.add(UserFactory())

        response = client.get(reverse("activities:stream"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 4


class TestActivityTimelineView:
    def test_get(self, client, member):
        PostFactory(community=member.community, owner=member.member)
        EventFactory(community=member.community, owner=member.member)

        response = client.get(reverse("activities:timeline"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2
        assert response.context["object_list"][0]["month"]


class TestActivityDraftsView:
    def test_get(self, client, member):
        PostFactory(community=member.community, owner=member.member)
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
            published=None,
        )
        PostFactory(
            community=member.community, owner=member.member, published=None
        )
        EventFactory(
            community=member.community, owner=member.member, published=None
        )

        response = client.get(reverse("activities:drafts"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2


class TestActivitySearchView:
    def test_get(self, client, member, transactional_db):
        PostFactory(
            community=member.community, title="test", owner=member.member
        )
        EventFactory(
            community=member.community, title="test", owner=member.member
        )

        response = client.get(reverse("activities:search"), {"q": "test"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_hashtag(self, client, member, transactional_db):
        member = MembershipFactory(community=member.community)
        PostFactory(
            community=member.community,
            description="#testme",
            owner=member.member,
        )
        response = client.get(reverse("activities:search"), {"q": "#testme"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1

    def test_get_if_search_string_empty(self, client, member):

        response = client.get(reverse("activities:search"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0


class TestTagAutocompleteListView:
    def test_get(self, client, member):

        PostFactory(community=member.community, owner=member.member).tags.add(
            "movies"
        )
        EventFactory(community=member.community, owner=member.member).tags.add(
            "movies"
        )
        PhotoFactory(community=member.community, owner=member.member).tags.add(
            "movies"
        )

        response = client.get(
            reverse("activities:tag_autocomplete_list"), {"q": "movie"}
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestTagFollowView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        response = client.post(reverse("activities:tag_follow", args=[tag.id]))
        assert response.url == reverse(
            "activities:tag_detail", args=[tag.slug]
        )
        assert tag in member.member.following_tags.all()


class TestTagUnfollowView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        member.member.following_tags.add(tag)
        response = client.post(
            reverse("activities:tag_unfollow", args=[tag.id])
        )
        assert response.url == reverse(
            "activities:tag_detail", args=[tag.slug]
        )
        assert tag not in member.member.following_tags.all()


class TestTagBlockView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        response = client.post(reverse("activities:tag_block", args=[tag.id]))
        assert response.url == reverse(
            "activities:tag_detail", args=[tag.slug]
        )
        assert tag in member.member.blocked_tags.all()


class TestTagUnblockView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        post.tags.set("movies")
        tag = Tag.objects.get()
        member.member.blocked_tags.add(tag)
        response = client.post(
            reverse("activities:tag_unblock", args=[tag.id])
        )
        assert response.url == reverse(
            "activities:tag_detail", args=[tag.slug]
        )
        assert tag not in member.member.blocked_tags.all()


class TestTagListView:
    def test_get(self, client, member):
        PostFactory(community=member.community, owner=member.member).tags.add(
            "movies"
        )

        response = client.get(reverse("activities:tag_list"))
        assert len(response.context["object_list"]) == 1


class TestFollowingTagListView:
    def test_get(self, client, member):
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        ).tags.add("movies")
        member.member.following_tags.add(Tag.objects.get(name="movies"))

        response = client.get(reverse("activities:following_tag_list"))
        assert len(response.context["object_list"]) == 1


class TestBlockedTagListView:
    def test_get(self, client, member):
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        ).tags.add("movies")
        member.member.blocked_tags.add(Tag.objects.get(name="movies"))

        response = client.get(reverse("activities:blocked_tag_list"))
        assert len(response.context["object_list"]) == 1


class TestTagDetailView:
    def test_get(self, client, member):
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        ).tags.add("movies")
        response = client.get(
            reverse("activities:tag_detail", args=["movies"])
        )
        assert response.context["tag"].name == "movies"
        assert len(response.context["object_list"]) == 1
