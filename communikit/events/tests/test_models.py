# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import geocoder
import pytest

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import force_str

from pytest_mock import MockFixture

from communikit.communities.models import Community, Membership
from communikit.events.models import Event
from communikit.events.tests.factories import EventFactory
from communikit.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestEventModel:
    def test_get_absolute_url(self, event: Event):
        assert event.get_absolute_url() == f"/events/{event.id}/"

    def test_get_domain_if_no_url(self):
        assert Event().get_domain() is None

    def test_get_domain_if_url(self):
        assert Event(url="http://google.com").get_domain() == "google.com"

    def test_notify(self, community: Community):
        owner = UserFactory(username="owner")
        moderator = UserFactory()
        mentioned = UserFactory(username="danjac")

        Membership.objects.create(
            member=owner, community=community, role=Membership.ROLES.moderator
        )
        Membership.objects.create(
            member=moderator,
            community=community,
            role=Membership.ROLES.moderator,
        )
        Membership.objects.create(
            member=mentioned, community=community, role=Membership.ROLES.member
        )

        event = EventFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner",
        )
        notifications = event.notify(created=True)

        assert notifications[0].recipient == mentioned
        assert notifications[0].verb == "mentioned"

        assert notifications[1].recipient == moderator
        assert notifications[1].verb == "created"

        # ensure saved to db
        assert event.notifications.count() == 2

        # change the description and remove the mention
        event.description = "hello!"
        event.save()

        notifications = event.notify(created=False)

        assert notifications[0].recipient == moderator
        assert notifications[0].verb == "updated"

        assert event.notifications.count() == 3

    def test_get_breadcrumbs(self, event: Event):
        assert event.get_breadcrumbs() == [
            ("/", "Home"),
            ("/events/", "Events"),
            (f"/events/{event.id}/", force_str(event.title)),
        ]

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
