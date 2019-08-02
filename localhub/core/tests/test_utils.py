# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.events.models import Event

pytestmark = pytest.mark.django_db


class TestTracker:
    def test_changed(self, event: Event):
        assert not event.location_tracker.changed()
        event.locality = "Helsinki"
        event.save()
        assert event.location_tracker.changed()
