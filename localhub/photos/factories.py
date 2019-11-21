# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

import factory
from factory import DjangoModelFactory, Faker, SubFactory, LazyFunction

from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

from .models import Photo


class PhotoFactory(DjangoModelFactory):
    title = Faker("text")
    image = factory.django.ImageField()
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(datetime.now)

    class Meta:
        model = Photo
