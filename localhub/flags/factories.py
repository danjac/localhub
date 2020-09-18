# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from factory import SubFactory
from factory.django import DjangoModelFactory

# Localhub
from localhub.activities.posts.factories import PostFactory
from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

# Local
from .models import Flag


class FlagFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    moderator = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)

    class Meta:
        model = Flag
