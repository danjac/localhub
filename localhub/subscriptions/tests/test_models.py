# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import factory
import pytest

from django.db.models import signals

from localhub.communities.models import Community
from localhub.subscriptions.models import Subscription
from localhub.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestSubscriptionModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, community: Community):
        followed = UserFactory()
        follower = UserFactory()
        subscription = Subscription.objects.create(
            content_object=followed, subscriber=follower, community=community
        )
        notifications = subscription.notify([followed])
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == follower
        assert notification.recipient == followed
        assert notification.content_object == followed
        assert notification.verb == "subscribe"
