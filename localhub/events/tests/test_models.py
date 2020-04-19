# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import force_str

import pytest
import pytz

from localhub.communities.factories import MembershipFactory
from localhub.users.factories import UserFactory

from ..factories import EventFactory
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventManager:
    def test_relevance_if_starts_in_future(self):
        EventFactory(starts=timezone.now() + timedelta(days=30))

        event = Event.objects.with_relevance().first()
        assert event.relevance == 1

    def test_relevance_if_starts_in_future_and_canceled(self):
        now = timezone.now()
        EventFactory(
            starts=now + timedelta(days=30), canceled=now,
        )

        event = Event.objects.with_relevance().first()
        assert event.relevance == -1

    def test_relevance_if_starts_in_past(self):
        EventFactory(starts=timezone.now() - timedelta(days=30))

        event = Event.objects.with_relevance().first()
        assert event.relevance == 0

    def test_relevance_if_starts_in_past_and_canceled(self):
        now = timezone.now()
        EventFactory(
            starts=now - timedelta(days=30), canceled=now,
        )

        event = Event.objects.with_relevance().first()
        assert event.relevance == -1

    def test_with_timedelta(self):

        now = timezone.now()
        first = EventFactory(starts=now + timedelta(days=30))
        second = EventFactory(starts=now + timedelta(days=15))
        third = EventFactory(starts=now - timedelta(days=20))
        fourth = EventFactory(starts=now - timedelta(days=5))

        events = Event.objects.with_timedelta().order_by("timedelta")

        assert events[0] == fourth
        assert events[1] == second
        assert events[2] == third
        assert events[3] == first

    def test_event_num_attendees_if_none(self, event):
        first = Event.objects.with_num_attendees().first()
        assert first.num_attendees == 0

    def test_event_num_attendees_if_any(self, event, user):
        event.attendees.add(user)
        first = Event.objects.with_num_attendees().first()
        assert first.num_attendees == 1

    def test_is_attending_if_anonymous(self, event, anonymous_user):
        first = Event.objects.is_attending(anonymous_user).first()
        assert not first.is_attending

    def test_is_attending_if_another_event(self, event, user):
        other = EventFactory()
        other.attendees.add(user)
        first = Event.objects.is_attending(user).get(pk=event.id)
        assert not first.is_attending
        second = Event.objects.is_attending(user).get(pk=other.id)
        assert second.is_attending

    def test_is_attending_if_true(self, event, user):
        event.attendees.add(user)
        first = Event.objects.is_attending(user).first()
        assert first.is_attending

    def test_is_attending_if_false(self, event, user):
        first = Event.objects.is_attending(user).first()
        assert not first.is_attending

    def test_with_common_annotations(self, event):
        member = MembershipFactory(community=event.community).member
        first = Event.objects.with_common_annotations(member, event.community).first()
        assert hasattr(first, "is_attending")
        assert hasattr(first, "num_attendees")


class TestEventModel:
    def test_has_not_started(self):
        event = Event(starts=timezone.now() + timedelta(days=30))
        assert not event.has_started()

    def test_has_started(self):
        event = Event(starts=timezone.now() - timedelta(days=30))
        assert event.has_started()

    def test_is_attendable(self):
        event = EventFactory()
        assert event.is_attendable()

    def test_is_attendable_if_has_started(self):
        event = EventFactory(starts=timezone.now() - timedelta(days=30))
        assert not event.is_attendable()

    def test_is_attendable_if_not_public(self):
        event = EventFactory(published=None)
        assert not event.is_attendable()

    def test_is_attendable_if_deleted(self):
        event = EventFactory(deleted=timezone.now())
        assert not event.is_attendable()

    def test_is_attendable_if_canceled(self):
        event = EventFactory(canceled=timezone.now())
        assert not event.is_attendable()

    def test_get_starts_with_tz(self):
        event = EventFactory(timezone=pytz.timezone("Europe/Helsinki"))
        assert event.get_starts_with_tz().tzinfo.zone == "Europe/Helsinki"

    def test_get_ends_with_tz_if_none(self):
        event = EventFactory(ends=None)
        assert event.get_ends_with_tz() is None

    def test_get_ends_with_tz(self):
        event = EventFactory(
            ends=timezone.now() + datetime.timedelta(days=30),
            timezone=pytz.timezone("Europe/Helsinki"),
        )

        assert event.get_ends_with_tz().tzinfo.zone == "Europe/Helsinki"

    def test_get_absolute_url(self, event):
        assert event.get_absolute_url().startswith(f"/events/{event.id}/")

    def test_get_domain_if_no_url(self):
        assert Event().get_domain() == ""

    def test_get_domain_if_url(self):
        assert Event(url="http://google.com").get_domain() == "google.com"

    def test_clean_if_ok(self):
        event = Event(starts=timezone.now(), ends=timezone.now() + timedelta(days=3))
        event.clean()

    def test_clean_if_ends_before_starts(self):
        event = Event(starts=timezone.now(), ends=timezone.now() - timedelta(days=3))
        with pytest.raises(ValidationError):
            event.clean()

    def test_get_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.get_location() == "Areenankuja 1, 00240 Helsinki, Uusimaa, Finland"
        ), "location property should include all event location fields"

    def test_get_location_if_empty(self):
        assert Event().get_location() == ""

    def test_get_full_location(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert event.get_full_location() == (
            "Hartwall Arena, Areenankuja 1, 00240 Helsinki, Uusimaa, Finland"
        ), "location should include all event location fields plus venue"

    def test_get_geocoder_location(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert event.get_geocoder_location() == (
            {
                "street": "Areenankuja 1",
                "city": "Helsinki",
                "postalcode": "00240",
                "country": "Finland",
            }
        ), "location should include street, postcode, country name and city"

    def test_get_geocoder_location_if_missing_data(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.get_geocoder_location() is None
        ), "location should be None if any missing fields"

    def test_location_no_country(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
        )
        assert (
            event.get_location() == "Areenankuja 1, 00240 Helsinki, Uusimaa"
        ), "location property should include all event location fields except country"  # noqa

    def test_partial_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.get_location() == "Areenankuja 1, Helsinki, Uusimaa, Finland"
        ), "location property should include all available location fields"

    def test_to_ical(self, event):
        result = force_str(event.to_ical())
        assert "DTSTART" in result

    def test_notify_on_attend_if_owner(self, event):
        assert len(event.notify_on_attend(event.owner)) == 0

    def test_notify_on_attend_if_member(self, event, member):
        notifications = event.notify_on_attend(member.member)
        assert len(notifications) == 1
        assert notifications[0].recipient == event.owner
        assert notifications[0].actor == member.member
        assert notifications[0].verb == "attend"

    def test_notify_on_cancel_if_owner(self, event):
        event.attendees.add(event.owner)
        assert len(event.notify_on_cancel(event.owner)) == 0

    def test_notify_on_cancel_by_moderator_if_owner_attending(self, event, moderator):
        event.attendees.add(event.owner)

        notifications = event.notify_on_cancel(moderator.member)
        assert len(notifications) == 1
        assert notifications[0].recipient == event.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "cancel"

    def test_notify_on_cancel_by_moderator_if_owner_not_attending(
        self, event, moderator
    ):
        notifications = event.notify_on_cancel(moderator.member)
        assert len(notifications) == 1
        assert notifications[0].recipient == event.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "cancel"

    def test_notify_on_cancel_if_attendee(self, event, member):
        event.attendees.add(member.member)
        notifications = event.notify_on_cancel(event.owner)
        assert len(notifications) == 1
        assert notifications[0].recipient == member.member
        assert notifications[0].actor == event.owner
        assert notifications[0].verb == "cancel"

    def test_notify_on_cancel_if_attendee_not_member(self, event):
        event.attendees.add(UserFactory())
        assert len(event.notify_on_cancel(event.owner)) == 0
