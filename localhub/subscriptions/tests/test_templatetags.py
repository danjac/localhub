# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.communities.models import Community
from localhub.subscriptions.models import Subscription
from localhub.subscriptions.templatetags.subscriptions_tags import (
    is_subscribed,
)
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestIsSubscribed:
    def test_user_anonymous(self):
        assert not is_subscribed(AnonymousUser(), UserFactory())

    def test_is_subscribed(self, community: Community):
        user = UserFactory()
        sub = Subscription.objects.create(
            community=community, content_object=user, subscriber=UserFactory()
        )
        assert is_subscribed(sub.subscriber, user)

    def test_is_not_subscribed(self):
        assert not is_subscribed(UserFactory(), UserFactory())
        pass
