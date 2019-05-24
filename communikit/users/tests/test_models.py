# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth import get_user_model

from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestUserManager:
    def test_match_usernames(self):
        user_1 = UserFactory(username="first")
        user_2 = UserFactory(username="second")
        user_3 = UserFactory(username="third")

        names = ["second", "FIRST", "SEconD"]  # duplicate

        users = User.objects.match_usernames(names)
        assert len(users) == 2
        assert user_1 in users
        assert user_2 in users
        assert user_3 not in users


class TestUserModel:
    def _test_get_profile_url(self, user: User):
        assert user.get_profile_url() == f"/profile/{user.username}/"
