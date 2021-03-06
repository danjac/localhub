# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import http

# Django
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str

# Third Party Libraries
import pytest

# Localhub
from localhub.communities.factories import MembershipFactory
from localhub.likes.factories import LikeFactory
from localhub.likes.models import Like

# Local
from ..factories import EventFactory
from ..models import Event

pytestmark = pytest.mark.django_db


@pytest.fixture
def event_for_member(member):
    return EventFactory(owner=member.member, community=member.community)


class TestEventCreateView:
    def test_get(self, client, member):
        response = client.get(reverse("events:create"))
        assert response.status_code == http.HTTPStatus.OK

    def test_post(self, client, member, send_webpush_mock):
        response = client.post(
            reverse("events:create"),
            {
                "title": "test",
                "description": "test",
                "starts_0": "2/2/2020",
                "starts_1": "10:00",
                "ends_0": "2/2/2020",
                "ends_1": "10:00",
                "timezone": "Europe/Helsinki",
            },
        )
        event = Event.objects.get()
        assert response.url == event.get_absolute_url()
        assert event.owner == member.member
        assert event.community == member.community


class TestEventListView:
    def test_get(self, client, member):
        EventFactory.create_batch(
            3,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("events:list"))
        assert response.status_code == http.HTTPStatus.OK
        assert len(dict(response.context_data or {})["object_list"]) == 3


class TestEventUpdateView:
    def test_get(self, client, event_for_member):
        response = client.get(reverse("events:update", args=[event_for_member.id]))
        assert response.status_code == http.HTTPStatus.OK

    def test_post(self, client, event_for_member, send_webpush_mock):
        response = client.post(
            reverse("events:update", args=[event_for_member.id]),
            {
                "title": "UPDATED",
                "description": event_for_member.description,
                "starts_0": "2/2/2020",
                "starts_1": "10:00",
                "ends_0": "2/2/2020",
                "ends_1": "10:00",
                "timezone": "Europe/Helsinki",
            },
        )
        event_for_member.refresh_from_db()
        assert response.url == event_for_member.get_absolute_url()
        assert event_for_member.title == "UPDATED"


class TestEventDeleteView:
    def test_post(self, client, event_for_member):
        response = client.post(reverse("events:delete", args=[event_for_member.id]))
        assert response.url == settings.HOME_PAGE_URL
        assert Event.objects.count() == 0


class TestEventDetailView:
    def test_get(self, client, event, member):
        response = client.get(
            event.get_absolute_url(), HTTP_HOST=event.community.domain
        )
        assert response.status_code == http.HTTPStatus.OK
        assert "comment_form" in dict(response.context or {})


class TestEventLikeView:
    def test_post(self, client, member, send_webpush_mock):
        event = EventFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(reverse("events:like", args=[event.id]))
        assert response.url == event.get_absolute_url()
        like = Like.objects.get()
        assert like.user == member.member


class TestEventDislikeView:
    def test_post(self, client, member):
        event = EventFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        LikeFactory(
            user=member.member,
            content_object=event,
            community=event.community,
            recipient=event.owner,
        )
        response = client.post(reverse("events:dislike", args=[event.id]))
        assert response.url == event.get_absolute_url()
        assert Like.objects.count() == 0


class TestEventDownloadView:
    def test_get(self, client, event, member):
        response = client.get(
            reverse("events:download", args=[event.id]),
            HTTP_HOST=event.community.domain,
        )
        assert response.status_code == http.HTTPStatus.OK
        assert "DTSTART" in force_str(response.content)


class TestEventCancelView:
    def test_post(self, client, event_for_member, send_webpush_mock):
        response = client.post(reverse("events:cancel", args=[event_for_member.id]))
        assert response.url == event_for_member.get_absolute_url()
        event_for_member.refresh_from_db()
        assert event_for_member.canceled


class TestEventAttendView:
    def test_post(self, client, event, member, send_webpush_mock):
        response = client.post(reverse("events:attend", args=[event.id]))
        assert response.status_code == http.HTTPStatus.OK
        assert member.member in event.attendees.all()


class TestEventUnattendView:
    def test_post(self, client, event, member, send_webpush_mock):
        event.attendees.add(member.member)
        response = client.post(reverse("events:unattend", args=[event.id]))
        assert response.status_code == http.HTTPStatus.OK
        assert member.member not in event.attendees.all()


class TestEventCalendarView:
    def test_get_calendar_view(self, client, event, member):
        response = client.get(
            reverse(
                "events:calendar",
            ),
            {"month": event.starts.month, "year": event.starts.year},
        )
        assert response.status_code == http.HTTPStatus.OK
        assert "current_date" not in response.context
        assert len(response.context["events"]) == 1

    def test_get_calendar_view_this_month(self, client, member):
        now = timezone.now()
        response = client.get(
            reverse(
                "events:calendar",
            ),
            {"month": now.month, "year": now.year},
        )
        assert response.status_code == http.HTTPStatus.OK
        assert "current_date" not in response.context
        assert response.context["is_current_month"]

    def test_get_calendar_view_with_invalid_date(self, client, event, member):
        response = client.get(
            reverse(
                "events:calendar",
            ),
            {"month": 13, "year": event.starts.year},
        )
        assert response.status_code == http.HTTPStatus.NOT_FOUND

    def test_get_date_view(self, client, event, member):
        response = client.get(
            reverse(
                "events:calendar",
            ),
            {
                "month": event.starts.month,
                "year": event.starts.year,
                "day": event.starts.day,
            },
        )
        assert response.status_code == http.HTTPStatus.OK
        assert "current_date" in response.context
        assert len(response.context["events"]) == 1

    def test_get_date_view_with_invalid_date(self, client, event, member):
        response = client.get(
            reverse(
                "events:calendar",
            ),
            {"month": event.starts.month, "year": event.starts.year, "day": 32},
        )
        assert response.status_code == http.HTTPStatus.NOT_FOUND
