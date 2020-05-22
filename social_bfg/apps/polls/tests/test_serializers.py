# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..factories import AnswerFactory
from ..serializers import PollSerializer

pytestmark = pytest.mark.django_db


class TestPollSerializer:
    def test_serialize_photo(self, poll):
        AnswerFactory.create_batch(3, poll=poll)
        data = PollSerializer(poll).data
        assert data["title"] == poll.title
        assert len(data["answers"]) == 3
        assert data["endpoints"]["detail"].endswith(f"/api/polls/{poll.id}/")
