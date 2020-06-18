# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from factory import DjangoModelFactory, SubFactory

# Localhub
# Social-BFG
from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.posts.factories import PostFactory
from localhub.apps.users.factories import UserFactory

# Local
from .models import Notification


class NotificationFactory(DjangoModelFactory):
    actor = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    content_object = SubFactory(PostFactory)
    verb = "mention"

    class Meta:
        model = Notification
