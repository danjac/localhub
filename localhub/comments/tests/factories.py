# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

from ..models import Comment


class CommentFactory(DjangoModelFactory):
    content = Faker("text")
    owner = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)

    class Meta:
        model = Comment
