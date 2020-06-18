# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.utils import timezone

# Third Party Libraries
import factory
from factory import DjangoModelFactory, Faker, LazyFunction, SubFactory

# Localhub
# Social-BFG
from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.users.factories import UserFactory

# Local
from .models import Photo


class PhotoFactory(DjangoModelFactory):
    title = Faker("text")
    image = factory.django.ImageField()
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    class Meta:
        model = Photo
