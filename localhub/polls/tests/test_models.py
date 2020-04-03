# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from localhub.communities.factories import MembershipFactory

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


class TestPollModel:
    def test_notify_on_vote(self, poll, send_webpush_mock):
        voter = MembershipFactory(community=poll.community).member
        notifications = poll.notify_on_vote(voter)
        assert len(notifications) == 1

    def test_notify_on_vote_if_owner(self, poll, send_webpush_mock):
        notifications = poll.notify_on_vote(poll.owner)
        assert len(notifications) == 0
