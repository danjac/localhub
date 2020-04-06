# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse

from ..factories import AnswerFactory, PollFactory
from ..models import Poll

pytestmark = pytest.mark.django_db


class TestPollListView:
    def test_get(self, client, member):
        PollFactory.create_batch(3, community=member.community, owner=member.member)
        response = client.get(reverse("polls:list"))
        assert len(response.context["object_list"]) == 3


class TestPollCreateView:
    def test_get(self, client, member):
        response = client.get(reverse("polls:create"))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        response = client.post(
            reverse("polls:create"),
            {
                "title": "test",
                "description": "test",
                "answers-0-description": "answer-one",
                "answers-1-description": "answer-two",
                "answers-TOTAL_FORMS": 3,
                "answers-INITIAL_FORMS": 0,
                "answers-MIN_NUM_FORMS": 0,
                "answers-MAX_NUM_FORMS": 4,
            },
        )
        poll = Poll.objects.get()
        assert response.url == poll.get_absolute_url()
        assert poll.owner == member.member
        assert poll.community == member.community

        assert poll.answers.count() == 2


class TestPollUpdateView:
    def test_get(self, client, member):
        poll = PollFactory(community=member.community, owner=member.member)
        response = client.get(reverse("polls:update", args=[poll.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        poll = PollFactory(community=member.community, owner=member.member)
        first_answer = AnswerFactory(poll=poll, description="answer-one")
        second_answer = AnswerFactory(poll=poll, description="answer-two")
        response = client.post(
            reverse("polls:update", args=[poll.id]),
            {
                "title": "UPDATED",
                "description": poll.description,
                "answers-TOTAL_FORMS": 3,
                "answers-INITIAL_FORMS": 2,
                "answers-MIN_NUM_FORMS": 0,
                "answers-MAX_NUM_FORMS": 4,
                "answers-0-description": "answer-one!",
                "answers-0-poll": poll.id,
                "answers-0-id": first_answer.id,
                "answers-1-description": "answer-two",
                "answers-1-poll": poll.id,
                "answers-1-id": second_answer.id,
                "answers-2-description": "answer-three",
            },
        )
        poll.refresh_from_db()
        assert response.url == poll.get_absolute_url()
        assert poll.title == "UPDATED"

        answers = poll.answers.order_by("id")
        assert answers[0].description == "answer-one!"
        assert answers[1].description == "answer-two"
        assert answers[2].description == "answer-three"


class TestPollDetailView:
    def test_get(self, client, poll, member):
        response = client.get(poll.get_absolute_url(), HTTP_HOST=poll.community.domain)
        assert response.status_code == 200
        assert "comment_form" in response.context


class TestAnswerVoteView:
    def test_post(self, client, member, send_webpush_mock):
        poll = PollFactory(community=member.community)
        answer = AnswerFactory(poll=poll)
        voted = AnswerFactory(poll=poll)
        voted.voters.add(member.member)
        response = client.post(reverse("polls:vote", args=[answer.id]))
        assert response.status_code == 200
        assert answer.voters.first() == member.member
        # original vote should be removed
        assert voted.voters.count() == 0
