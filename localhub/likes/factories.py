# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from factory import DjangoModelFactory, SubFactory

from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.users.factories import UserFactory
from localhub.posts.factories import PostFactory

from .models import Like


class LikeFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)

    class Meta:
        model = Like
