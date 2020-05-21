# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..serializers import EventSerializer

pytestmark = pytest.mark.django_db


class TestEventSerializer:
    def test_serialize_event(self, event):
        data = EventSerializer(event).data
        assert data["title"] == event.title
