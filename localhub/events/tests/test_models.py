# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from datetime import timedelta

import pytest
import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import force_str

from localhub.communities.factories import MembershipFactory
from ..factories import EventFactory
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventManager:
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
