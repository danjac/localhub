# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

from .models import Post


class PostFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Post
