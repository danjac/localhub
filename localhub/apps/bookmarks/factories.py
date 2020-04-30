# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from factory import DjangoModelFactory, SubFactory

from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.posts.factories import PostFactory
from localhub.apps.users.factories import UserFactory

from .models import Bookmark


class BookmarkFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)

    class Meta:
        model = Bookmark
