# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from localhub.users.rules import is_self
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestIsSelf:
    def test_is_self(self, user: settings.AUTH_USER_MODEL):
        assert is_self(user, user)

    def test_if_anonymous(self, user: settings.AUTH_USER_MODEL):
        assert not is_self(AnonymousUser(), user)

    def test_if_other_user(self, user: settings.AUTH_USER_MODEL):
        assert not is_self(UserFactory(), user)


class TestPermissions:
    def test_can_change_user(self, user: settings.AUTH_USER_MODEL):
        assert user.has_perm("users.change_user", user)
        assert not user.has_perm("users.change_user", UserFactory())

    def test_can_delete_user(self, user: settings.AUTH_USER_MODEL):
        assert user.has_perm("users.delete_user", user)
        assert not user.has_perm("users.change_user", UserFactory())

    def test_can_follow_user(self, user: settings.AUTH_USER_MODEL):
        assert not user.has_perm("users.follow_user", user)
        assert user.has_perm("users.follow_user", UserFactory())

    def test_can_block_user(self, user: settings.AUTH_USER_MODEL):
        assert not user.has_perm("users.block_user", user)
        assert user.has_perm("users.block_user", UserFactory())

    def test_can_follow_tag(self, user: settings.AUTH_USER_MODEL):
        assert user.has_perm("users.follow_tag")

    def test_can_block_tag(self, user: settings.AUTH_USER_MODEL):
        assert user.has_perm("users.block_tag")
