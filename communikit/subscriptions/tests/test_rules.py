# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings

from communikit.communities.models import Community, Membership

pytestmark = pytest.mark.django_db


class TestHasCreateSubscriptionPermission:
    def test_if_not_has_perm(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not user.has_perm(
            "subscriptions.create_subscription", community
        )

    def test_if_has_perm(self, member: Membership):
        assert member.member.has_perm(
            "subscriptions.create_subscription", member.community
        )
