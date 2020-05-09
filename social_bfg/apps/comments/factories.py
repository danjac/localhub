# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from factory import DjangoModelFactory, Faker, SubFactory

# Social-BFG
from social_bfg.apps.communities.factories import CommunityFactory
from social_bfg.apps.posts.factories import PostFactory
from social_bfg.apps.users.factories import UserFactory

# Local
from .models import Comment


class CommentFactory(DjangoModelFactory):
    content = Faker("text")
    owner = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)

    class Meta:
        model = Comment
