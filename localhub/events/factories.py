# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone
from factory import DjangoModelFactory, Faker, LazyFunction, SubFactory
from factory.fuzzy import FuzzyDateTime

from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

from .models import Event


class EventFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    starts = FuzzyDateTime(timezone.now())

    class Meta:
        model = Event
