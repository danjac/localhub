# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.urls import reverse
from django.test.client import Client

from taggit.models import Tag

from communikit.communities.models import Membership
from communikit.subscriptions.models import Subscription
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

class TestSubscribedUserListView:
    def test_get(self, client: Client, member: Membership):
        user = UserFactory()
        Membership.objects.create(member=user, community=member.community)
        Subscription.objects.create(
            content_object=user,
            subscriber=member.member,
            community=member.community,
        )
        response = client.get(reverse("subscriptions:user_list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestSubscribedTagListView:
    def test_get(self, client: Client, member: Membership):
        tag = Tag.objects.create(name="movies")
        Subscription.objects.create(
            content_object=tag,
            subscriber=member.member,
            community=member.community,
        )
        response = client.get(reverse("subscriptions:tag_list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
