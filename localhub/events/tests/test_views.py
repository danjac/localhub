# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.urls import reverse
from django.utils.encoding import force_str

from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.events.models import Event
from localhub.events.tests.factories import EventFactory
from localhub.likes.models import Like

pytestmark = pytest.mark.django_db


@pytest.fixture
def event_for_member(member):
    return EventFactory(owner=member.member, community=member.community)


class TestEventCreateView:
    def test_get(self, client, member):
        response = client.get(reverse("events:create"))
        assert response.status_code == 200

    def test_post(self, client, member, send_notification_webpush_mock):
        response = client.post(
            reverse("events:create"),
            {
                "title": "test",
                "description": "test",
                "starts_0": "2019-2-2",
                "starts_1": "10:00",
                "ends_0": "2019-2-2",
                "ends_1": "10:00",
                "timezone": "Europe/Helsinki",
            },
        )
        event = Event.objects.get()
        assert response.url == event.get_absolute_url()
        assert event.owner == member.member
        assert event.community == member.community


class TestEventListView:
    def test_get(self, client, community):
        EventFactory.create_batch(
            3,
            community=community,
            owner=MembershipFactory(community=community).member,
        )
        response = client.get(reverse("events:list"))
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 3


class TestEventUpdateView:
    def test_get(self, client, event_for_member):
        response = client.get(
            reverse("events:update", args=[event_for_member.id])
        )
        assert response.status_code == 200

    def test_post(
        self, client, event_for_member, send_notification_webpush_mock
    ):
        response = client.post(
            reverse("events:update", args=[event_for_member.id]),
            {
                "title": "UPDATED",
                "description": event_for_member.description,
                "starts_0": "2019-2-2",
                "starts_1": "10:00",
                "ends_0": "2019-2-2",
                "ends_1": "10:00",
                "timezone": "Europe/Helsinki",
            },
        )
        event_for_member.refresh_from_db()
        assert response.url == event_for_member.get_absolute_url()
        assert event_for_member.title == "UPDATED"


class TestEventDeleteView:
    def test_get(self, client, event_for_member):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("events:delete", args=[event_for_member.id])
        )
        assert response.status_code == 200

    def test_post(self, client, event_for_member):
        response = client.post(
            reverse("events:delete", args=[event_for_member.id])
        )
        assert response.url == reverse("activities:stream")
        assert Event.objects.count() == 0


class TestEventDetailView:
    def test_get(self, client, event):
        response = client.get(
            event.get_absolute_url(), HTTP_HOST=event.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" not in dict(response.context or {})

    def test_get_if_can_post_comment(self, client, event, login_user):
        Membership.objects.create(member=login_user, community=event.community)

        response = client.get(
            event.get_absolute_url(), HTTP_HOST=event.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" in dict(response.context or {})


class TestEventLikeView:
    def test_post(self, client, member, send_notification_webpush_mock):
        event = EventFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("events:like", args=[event.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = Like.objects.get()
        assert like.user == member.member


class TestEventDislikeView:
    def test_post(self, client, member):
        event = EventFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        Like.objects.create(
            user=member.member,
            content_object=event,
            community=event.community,
            recipient=event.owner,
        )
        response = client.post(
            reverse("events:dislike", args=[event.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert Like.objects.count() == 0


class TestEventDownloadView:
    def test_get(self, client, event):
        response = client.get(
            reverse("events:download", args=[event.id]),
            HTTP_HOST=event.community.domain,
        )
        assert response.status_code == 200
        assert "DTSTART" in force_str(response.content)
