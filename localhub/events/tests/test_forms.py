# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import datetime

# Third Party Libraries
import pytest
import pytz

# Local
from ..factories import EventFactory
from ..forms import EventForm

pytestmark = pytest.mark.django_db


class TestEventForm:
    def get_form_data(self, **values):
        return {
            "title": "test",
            "description": "test",
            "starts_0": "2/2/2020",
            "starts_1": "10:00",
            "ends_0": "2/2/2020",
            "ends_1": "10:00",
            "repeats_until_0": None,
            "repeats_until_1": None,
            "repeats": None,
            "timezone": "Europe/Helsinki",
            "street_address": "Olavinkatu 36",
            "locality": "Savonlinna",
            "postal_code": "57300",
            "country": "FI",
            **values,
        }

    def test_initial_with_correct_timezone_value(self):

        event = EventFactory(
            timezone=pytz.timezone("Europe/Helsinki"),
            starts=datetime.datetime(
                hour=10, day=1, year=2019, month=10, tzinfo=pytz.UTC
            ),
        )
        form = EventForm(instance=event)
        # assert form.initial["starts"].tzinfo == pytz.UTC
        assert form.initial["starts"].hour == 13

    def test_save_with_converted_utc(self):
        form = EventForm(self.get_form_data())
        assert form.is_valid()

        instance = form.save(commit=False)
        # check values converted
        assert instance.starts.tzinfo == pytz.UTC
        assert instance.starts.hour == 8
        assert instance.ends.tzinfo == pytz.UTC
        assert instance.ends.hour == 8

    def test_clear_geolocation_if_no_latlng(self):
        event = EventFactory(latitude=None, longitude=None)
        form = EventForm(instance=event)
        assert "clear_geolocation" not in form.fields

    def test_clear_geolocation_if_latlng(self):
        event = EventFactory(latitude=60, longitude=30)

        form = EventForm(
            self.get_form_data(clear_geolocation=True, fetch_geolocation=True),
            instance=event,
        )
        assert "clear_geolocation" in form.fields
        assert form.is_valid()

        instance = form.save(commit=False)
        assert instance.latitude is None
        assert instance.longitude is None

    def test_save_if_fetch_geolocation_valid(self, mocker):
        mocker.patch("localhub.events.forms.geocode", return_value=(60.1, 30.2))
        form = EventForm(self.get_form_data(fetch_geolocation=True))
        assert form.is_valid()

        instance = form.save(commit=False)
        assert instance.latitude == 60.1
        assert instance.longitude == 30.2

    def test_save_if_fetch_geolocation_invalid(self, mocker):
        mocker.patch("localhub.events.forms.geocode", return_value=(None, None))
        form = EventForm(self.get_form_data(fetch_geolocation=True))
        assert not form.is_valid()
