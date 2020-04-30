# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone

from factory import DjangoModelFactory, Faker, LazyFunction, SubFactory

from localhub.apps.users.factories import UserFactory
from localhub.communities.factories import CommunityFactory

from .models import Answer, Poll


class PollFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    class Meta:
        model = Poll


class AnswerFactory(DjangoModelFactory):
    description = Faker("text", max_nb_chars=100)
    poll = SubFactory(PollFactory)

    class Meta:
        model = Answer
