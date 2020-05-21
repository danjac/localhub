# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import status

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.apps.events.factories import EventFactory
from social_bfg.apps.polls.factories import AnswerFactory, PollFactory
from social_bfg.apps.posts.factories import PostFactory
from social_bfg.apps.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestDefaultStreamAPIView:
    def test_get_if_non_member(self, client, login_user, community):
        response = client.get("/api/streams/default/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_if_member(self, client, member):
        EventFactory(community=member.community, owner=member.member)
        PostFactory(community=member.community, owner=member.member)
        PostFactory(community=member.community, owner=member.member)
        poll = PollFactory(community=member.community, owner=member.member)

        for _ in range(3):
            answer = AnswerFactory(poll=poll)
            answer.voters.add(UserFactory())

        response = client.get("/api/streams/default/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 4
