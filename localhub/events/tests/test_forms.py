# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
import pytz
import pytest


from localhub.events.forms import EventForm
from localhub.events.tests.factories import EventFactory

pytestmark = pytest.mark.django_db


class TestEventForm:
    def test_initial_with_correct_timezone_value(self):

        event = EventFactory(
            timezone=pytz.timezone("Europe/Helsinki"),
            starts=datetime.datetime(
                hour=10, day=1, year=2019, month=10, tzinfo=pytz.UTC
            ),
        )
        form = EventForm(instance=event)
        assert form.initial["starts"].tzinfo == pytz.UTC
        assert form.initial["starts"].hour == 13

    def test_save_with_converted_utc(self):

        data = {
            "title": "test",
            "description": "test",
            "starts_0": "2019-2-2",
            "starts_1": "10:00",
            "ends_0": "2019-2-2",
            "ends_1": "10:00",
            "timezone": "Europe/Helsinki",
        }
        form = EventForm(data)
        instance = form.save(commit=False)
        # check values converted
        assert instance.starts.tzinfo == pytz.UTC
        assert instance.starts.hour == 8
        assert instance.ends.tzinfo == pytz.UTC
        assert instance.ends.hour == 8
