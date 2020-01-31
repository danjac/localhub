# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from ..factories import AnswerFactory
from ..models import Poll

pytestmark = pytest.mark.django_db


class TestPollManager:
    def test_with_answers(self, poll, user):
        answer = AnswerFactory(poll=poll)
        answer.voters.add(user)

        poll = Poll.objects.with_answers().first()
        assert poll.total_num_votes == 1

        answer = poll.answers.all()[0]
        assert answer.num_votes == 1
