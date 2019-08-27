# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
import geocoder
import pytz
import pytest

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import force_str

from localhub.events.models import Event
from localhub.events.tests.factories import EventFactory


pytestmark = pytest.mark.django_db


class TestEventModel:
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
        assert Event().get_domain() is None

    def test_get_domain_if_url(self):
        assert Event(url="http://google.com").get_domain() == "google.com"

    def test_clean_if_ok(self):
        event = Event(
            starts=timezone.now(), ends=timezone.now() + timedelta(days=3)
        )
        event.clean()

    def test_clean_if_ends_before_starts(self):
        event = Event(
            starts=timezone.now(), ends=timezone.now() - timedelta(days=3)
        )
        with pytest.raises(ValidationError):
            event.clean()

    def test_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.location
            == "Areenankuja 1, Helsinki, 00240, Uusimaa, Finland"
        ), "location property should include all event location fields"

    def test_full_location(self):
        event = Event(
            venue="Hartwall Arena",
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert event.full_location == (
            "Hartwall Arena, Areenankuja 1, "
            "Helsinki, 00240, Uusimaa, Finland"
        ), (
            "location property should include all event "
            "location fields plus venue"
        )

    def test_location_no_country(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
        )
        assert (
            event.location == "Areenankuja 1, Helsinki, 00240, Uusimaa"
        ), "location property should include all event location fields except country"  # noqa

    def test_partial_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.location == "Areenankuja 1, Helsinki, Uusimaa, Finland"
        ), "location property should include all available location fields"

    def test_update_coordinates_ok(self, mocker, event):
        class MockGoodOSMResult:
            lat = 60
            lng = 50

        mocker.patch("geocoder.osm", return_value=MockGoodOSMResult)

        event.street_address = "Areenankuja 1"
        event.locality = "Helsinki"
        event.region = "Uusimaa"
        event.country = "FI"

        assert event.update_coordinates() == (60, 50)

        assert event.latitude == 60
        assert event.longitude == 50

        geocoder.osm.assert_called_once_with(event.location)

    def test_update_coordinates_not_ok(self, mocker, event):
        class MockBadOSMResult:
            lat = None
            lng = None

        mocker.patch("geocoder.osm", return_value=MockBadOSMResult)

        event.street_address = "Areenankuja 1"
        event.locality = "Helsinki"
        event.region = "Uusimaa"
        event.country = "FI"

        assert event.update_coordinates() == (None, None)

        assert event.latitude is None
        assert event.longitude is None

        geocoder.osm.assert_called_once_with(event.location)

    def test_update_coordinates_location_empty(self, mocker, event):
        mocker.patch("geocoder.osm")

        assert event.update_coordinates() == (None, None)

        assert event.latitude is None
        assert event.longitude is None

        assert geocoder.osm.call_count == 0

    def test_to_ical(self, event):
        result = force_str(event.to_ical())
        assert "DTSTART" in result
