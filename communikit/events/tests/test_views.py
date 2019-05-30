# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Community, Membership
from communikit.events.models import Event
from communikit.events.tests.factories import EventFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def event_for_member(member: Membership) -> Event:
    return EventFactory(owner=member.member, community=member.community)


class TestEventCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("events:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        response = client.post(
            reverse("events:create"),
            {
                "title": "test",
                "description": "test",
                "starts_0": "2019-2-2",
                "starts_1": "10:00",
                "ends_0": "2019-2-2",
                "ends_1": "10:00",
            },
        )
        event = Event.objects.get()
        assert response.url == event.get_absolute_url()
        assert event.owner == member.member
        assert event.community == member.community


class TestEventListView:
    def test_get(self, client: Client, community: Community):
        EventFactory.create_batch(3, community=community)
        response = client.get(reverse("events:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


class TestEventUpdateView:
    def test_get(self, client: Client, event_for_member: Event):
        response = client.get(
            reverse("events:update", args=[event_for_member.id])
        )
        assert response.status_code == 200

    def test_post(self, client: Client, event_for_member: Event):
        response = client.post(
            reverse("events:update", args=[event_for_member.id]),
            {
                "title": "UPDATED",
                "description": event_for_member.description,
                "starts_0": "2019-2-2",
                "starts_1": "10:00",
                "ends_0": "2019-2-2",
                "ends_1": "10:00",
            },
        )
        assert response.url == event_for_member.get_absolute_url()
        event_for_member.refresh_from_db()
        assert event_for_member.title == "UPDATED"


class TestEventDeleteView:
    def test_get(self, client: Client, event_for_member: Event):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("events:delete", args=[event_for_member.id])
        )
        assert response.status_code == 200

    def test_delete(self, client: Client, event_for_member: Event):
        response = client.delete(
            reverse("events:delete", args=[event_for_member.id])
        )
        assert response.url == reverse("activities:stream")
        assert Event.objects.count() == 0


class TestEventDetailView:
    def test_get(self, client: Client, event: Event):
        response = client.get(
            reverse("events:detail", args=[event.id]),
            HTTP_HOST=event.community.domain,
        )
        assert response.status_code == 200
        assert "comment_form" not in response.context

    def test_get_if_can_post_comment(
        self,
        client: Client,
        event: Event,
        login_user: settings.AUTH_USER_MODEL,
    ):
        Membership.objects.create(member=login_user, community=event.community)

        response = client.get(
            reverse("events:detail", args=[event.id]),
            HTTP_HOST=event.community.domain,
        )
        assert response.status_code == 200
        assert "comment_form" in response.context


class TestEventLikeView:
    def test_post(self, client: Client, member: Membership):
        event = EventFactory(community=member.community)
        response = client.post(
            reverse("events:like", args=[event.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = event.like_set.get()
        assert like.user == member.member


class TestEventDislikeView:
    def test_post(self, client: Client, member: Membership):
        event = EventFactory(community=member.community)
        event.like_set.create(user=member.member)
        response = client.post(
            reverse("events:dislike", args=[event.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert event.like_set.count() == 0
