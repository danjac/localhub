# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from communikit.communities.models import Membership

pytestmark = pytest.mark.django_db


User = get_user_model()


class TestUserDetailView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(
            reverse("users:detail", args=[member.member.username])
        )
        assert response.status_code == 200


class TestUserUpdateView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get(reverse("users:update"))
        assert response.status_code == 200

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        url = reverse("users:update")
        response = client.post(url, {"name": "New Name"})
        assert response.url == url
        login_user.refresh_from_db()
        assert login_user.name == "New Name"


class TestUserDeleteView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get(reverse("users:delete"))
        assert response.status_code == 200

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.post(reverse("users:delete"))
        assert response.url == "/account/login/"
        assert User.objects.filter(username=login_user.username).count() == 0
