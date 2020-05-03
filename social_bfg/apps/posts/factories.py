# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils import timezone

# Third Party Libraries
from factory import DjangoModelFactory, Faker, LazyFunction, SubFactory

# Social-BFG
from social_bfg.apps.communities.factories import CommunityFactory
from social_bfg.apps.users.factories import UserFactory

from .models import Post


class PostFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    class Meta:
        model = Post
