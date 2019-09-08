# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from factory import DjangoModelFactory, SubFactory, Faker

from localhub.communities.tests.factories import CommunityFactory
from localhub.polls.models import Answer, Poll
from localhub.users.tests.factories import UserFactory


class PollFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Poll


class AnswerFactory(DjangoModelFactory):
    description = Faker("text", max_nb_chars=100)
    poll = SubFactory(PollFactory)

    class Meta:
        model = Answer
