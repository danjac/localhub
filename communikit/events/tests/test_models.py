# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import geocoder
import pytest

from pytest_mock import MockFixture

from communikit.events.models import Event

pytestmark = pytest.mark.django_db


class TestEventModel:
    def test_get_absolute_url(self, event: Event):
        assert event.get_absolute_url() == f"/events/{event.id}/"

    def test_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            postal_code="00240",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.location == "Areenankuja 1, Helsinki, 00240, Uusimaa, FI"
        ), "location property should include all event location fields"

    def test_partial_location(self):
        event = Event(
            street_address="Areenankuja 1",
            locality="Helsinki",
            region="Uusimaa",
            country="FI",
        )
        assert (
            event.location == "Areenankuja 1, Helsinki, Uusimaa, FI"
        ), "location property should include all available location fields"

    def test_update_coordinates_ok(self, mocker: MockFixture, event: Event):
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

    def test_update_coordinates_not_ok(
        self, mocker: MockFixture, event: Event
    ):
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

    def test_update_coordinates_location_empty(
        self, mocker: MockFixture, event: Event
    ):
        mocker.patch("geocoder.osm")

        assert event.update_coordinates() == (None, None)

        assert event.latitude is None
        assert event.longitude is None

        assert geocoder.osm.call_count == 0
