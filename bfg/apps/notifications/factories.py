# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from factory import DjangoModelFactory, SubFactory

from bfg.apps.communities.factories import CommunityFactory
from bfg.apps.posts.factories import PostFactory
from bfg.apps.users.factories import UserFactory

from .models import Notification


class NotificationFactory(DjangoModelFactory):
    actor = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)
    verb = "mention"

    class Meta:
        model = Notification