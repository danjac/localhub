# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from factory import DjangoModelFactory, SubFactory

# Localhub
from localhub.communities.factories import CommunityFactory
from localhub.posts.factories import PostFactory
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
