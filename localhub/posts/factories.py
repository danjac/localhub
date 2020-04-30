# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone

from factory import DjangoModelFactory, Faker, LazyFunction, SubFactory

from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.users.factories import UserFactory

from .models import Post


class PostFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    class Meta:
        model = Post
