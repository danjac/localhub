# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from localhub.polls.models import Answer, Poll

pytestmark = pytest.mark.django_db


class TestPollManager:
    def test_with_voting_counts(self, poll, user):
        answer = Answer.objects.create(poll=poll, description="test")
        answer.voters.add(user)

        poll = Poll.objects.with_voting_counts().first()
        assert poll.total_num_votes == 1

        answer = poll.answers.all()[0]
        assert answer.num_votes == 1
