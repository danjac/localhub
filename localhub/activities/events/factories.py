# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
from datetime import timedelta

# Django
from django.utils import timezone

# Third Party Libraries
from factory import Faker, LazyFunction, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime

# Localhub
from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

# Local
from .models import Event


class EventFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    starts = FuzzyDateTime(
        start_dt=timezone.now() + timedelta(days=30),
        end_dt=timezone.now() + timedelta(days=36),
    )

    class Meta:
        model = Event
