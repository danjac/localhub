# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.conf import settings
from django.urls import reverse
from taggit.models import Tag

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.events.factories import EventFactory
from localhub.photos.factories import PhotoFactory
from localhub.polls.factories import AnswerFactory, PollFactory
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityStreamView:
    def test_get_if_non_member(self, client, login_user, community):
        response = client.get(settings.LOCALHUB_HOME_PAGE_URL)
        assert response.url == reverse("community_welcome")

    def test_get_if_member(self, client, member):
        EventFactory(community=member.community, owner=member.member)
        PostFactory(community=member.community, owner=member.member)
        PostFactory(community=member.community, owner=member.member)
        poll = PollFactory(community=member.community, owner=member.member)

        for _ in range(3):
            answer = AnswerFactory(poll=poll)
            answer.voters.add(UserFactory())

        response = client.get(settings.LOCALHUB_HOME_PAGE_URL)
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


class TestActivityPrivateView:
    def test_get(self, client, member):
        PostFactory(community=member.community, owner=member.member)
        PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
            published=None,
        )
        PostFactory(community=member.community, owner=member.member, published=None)
        EventFactory(community=member.community, owner=member.member, published=None)

        response = client.get(reverse("activities:private"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2


class TestActivitySearchView:
    def test_get(self, client, member, transactional_db):
        PostFactory(community=member.community, title="test", owner=member.member)
        EventFactory(community=member.community, title="test", owner=member.member)

        response = client.get(reverse("activities:search"), {"q": "test"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_hashtag(self, client, member, transactional_db):
        member = MembershipFactory(community=member.community)
        PostFactory(
            community=member.community, description="#testme", owner=member.member,
        )
        response = client.get(reverse("activities:search"), {"q": "#testme"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1

    def test_get_if_search_string_empty(self, client, member):

        response = client.get(reverse("activities:search"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 0
