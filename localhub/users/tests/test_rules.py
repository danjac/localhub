# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..factories import UserFactory
from ..rules import is_self

pytestmark = pytest.mark.django_db


class TestIsSelf:
    def test_is_self(self, user):
        assert is_self(user, user)

    def test_if_anonymous(self, user, anonymous_user):
        assert not is_self(anonymous_user, user)

    def test_if_other_user(self, user):
        assert not is_self(UserFactory(), user)


class TestPermissions:
    def test_can_change_user(self, user):
        assert user.has_perm("users.change_user", user)
        assert not user.has_perm("users.change_user", UserFactory())

    def test_can_delete_user(self, user):
        assert user.has_perm("users.delete_user", user)
        assert not user.has_perm("users.change_user", UserFactory())

    def test_can_follow_user(self, user):
        assert not user.has_perm("users.follow_user", user)
        assert user.has_perm("users.follow_user", UserFactory())

    def test_can_block_user(self, user):
        assert not user.has_perm("users.block_user", user)
        assert user.has_perm("users.block_user", UserFactory())

    def test_can_follow_tag(self, user):
        assert user.has_perm("users.follow_tag")

    def test_can_block_tag(self, user):
        assert user.has_perm("users.block_tag")

    def test_anonymous_can_change_user(self, user, anonymous_user):
        assert not anonymous_user.has_perm("users.change_user", user)

    def test_anonymous_can_delete_user(self, user, anonymous_user):
        assert not anonymous_user.has_perm("users.delete_user", user)

    def test_anonymous_can_follow_user(self, user, anonymous_user):
        assert not anonymous_user.has_perm("users.follow_user", user)

    def test_anonymous_can_block_user(self, user, anonymous_user):
        assert not anonymous_user.has_perm("users.block_user", user)

    def test_anonymous_can_follow_tag(self, user, anonymous_user):
        assert not anonymous_user.has_perm("users.follow_tag")

    def test_anonymous_can_block_tag(self, user, anonymous_user):
        assert not anonymous_user.has_perm("users.block_tag")
