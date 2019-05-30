# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress

from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self):

        user = get_user_model().objects.create_user(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.check_password("t3ZtP4s31")

    def test_create_superuser(self):

        user = get_user_model().objects.create_superuser(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.is_superuser
        assert user.is_staff

    def test_for_email_matching_email_field(self):

        user = UserFactory(email="test@gmail.com")
        assert (
            get_user_model().objects.for_email("test@gmail.com").first()
            == user
        )

    def test_for_email_matching_email_address_instance(self):

        user = UserFactory()
        EmailAddress.objects.create(user=user, email="test@gmail.com")
        assert (
            get_user_model().objects.for_email("test@gmail.com").first()
            == user
        )

    def test_matches_usernames(self):
        user_1 = UserFactory(username="first")
        user_2 = UserFactory(username="second")
        user_3 = UserFactory(username="third")

        names = ["second", "FIRST", "SEconD"]  # duplicate

        users = get_user_model().objects.matches_usernames(names)
        assert len(users) == 2
        assert user_1 in users
        assert user_2 in users
        assert user_3 not in users

        # check empty set returns no results
        assert get_user_model().objects.matches_usernames([]).count() == 0


class TestUserModel:
    def _test_get_profile_url(self, user: settings.AUTH_USER_MODEL):
        assert user.get_profile_url() == f"/profile/{user.username}/"
