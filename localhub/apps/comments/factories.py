# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from factory import DjangoModelFactory, Faker, SubFactory

# Localhub
# Social-BFG
from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.posts.factories import PostFactory
from localhub.apps.users.factories import UserFactory

# Local
from .models import Comment


class CommentFactory(DjangoModelFactory):
    content = Faker("text")
    owner = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)

    class Meta:
        model = Comment
