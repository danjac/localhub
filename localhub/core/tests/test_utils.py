# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.core.utils.functional import nested_getattr
from localhub.events.models import Event

pytestmark = pytest.mark.django_db


class Nested:
    a = 1


class SomeClass:
    nested = Nested()


class TestTracker:
    def test_changed(self, event: Event):
        assert not event.location_tracker.changed()
        event.locality = "Helsinki"
        event.save()
        assert event.location_tracker.changed()


class TestNestedGettattr:
    def test_exists(self):
        assert nested_getattr(SomeClass(), "nested.a") == 1

    def test_does_not_exist(self):
        with pytest.raises(AttributeError):
            nested_getattr(SomeClass(), "nested.b")

    def test_has_default(self):
        assert nested_getattr(SomeClass(), "nested.b", default=2) == 2
