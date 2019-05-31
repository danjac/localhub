# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings

from communikit.users.tests.factories import UserFactory

from communikit.communities.models import Community, Membership
from communikit.communities.rules import (
    is_admin,
    is_moderator,
    is_member,
    is_own_membership,
    is_membership_community_admin,
)

pytestmark = pytest.mark.django_db


class TestIsAdmin:
    def test_is_admin_if_user_not_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not is_admin.test(user, community)
        assert not is_moderator.test(user, community)
        assert not is_member.test(user, community)

    def test_is_admin_if_user_is_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert is_admin.test(user, community)
        assert is_moderator.test(user, community)
        assert is_member.test(user, community)


class TestIsModerator:
    def test_is_moderator_if_user_not_moderator(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not is_admin.test(user, community)
        assert not is_moderator.test(user, community)
        assert not is_member.test(user, community)

    def test_is_moderator_if_user_is_moderator(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="moderator"
        )
        assert not is_admin.test(user, community)
        assert is_moderator.test(user, community)
        assert is_member.test(user, community)


class TestIsMember:
    def test_is_member_if_user_not_member(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not is_admin.test(user, community)
        assert not is_moderator.test(user, community)
        assert not is_member.test(user, community)

    def test_is_member_if_user_is_member(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert not is_admin.test(user, community)
        assert not is_moderator.test(user, community)
        assert is_member.test(user, community)


class TestIsOwnMembership:
    def test_is_own_membership_if_true(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            community=community, member=user, role="admin"
        )
        assert is_own_membership.test(user, membership)

    def test_is_own_membership_if_false(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            community=community, member=UserFactory(), role="admin"
        )
        assert not is_own_membership.test(user, membership)


class TestIsMembershipCommunityAdmin:
    def test_is_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            community=community, member=user, role="admin"
        )
        assert is_membership_community_admin.test(user, membership)

    def test_is_not_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            community=community, member=user, role="member"
        )
        assert not is_membership_community_admin.test(user, membership)


class TestCommunityPermissions:
    def test_can_manage_community_if_user_is_not_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not user.has_perm("communities.manage_community", community)

    def test_can_manage_community_if_user_is_admin(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert user.has_perm("communities.manage_community", community)


class TestMembershipPermissions:

    def test_can_change_membership_if_is_admin_and_is_other_membership(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="admin"
        )
        membership = Membership.objects.create(
            member=UserFactory(), community=community, role="admin"
        )
        assert user.has_perm("communities.change_membership", membership)

    def test_can_change_membership_if_is_admin_and_is_own_membership(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert not user.has_perm("communities.change_membership", membership)

    def test_can_delete_membership_if_is_admin_and_is_other_membership(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="admin"
        )
        membership = Membership.objects.create(
            member=UserFactory(), community=community, role="admin"
        )
        assert user.has_perm("communities.delete_membership", membership)

    def test_can_delete_membership_if_not_is_admin_and_is_other_membership(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Membership.objects.create(
            member=user, community=community, role="member"
        )
        membership = Membership.objects.create(
            member=UserFactory(), community=community, role="admin"
        )
        assert not user.has_perm("communities.delete_membership", membership)

    def test_can_delete_membership_if_not_is_admin_and_is_own_membership(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert user.has_perm("communities.delete_membership", membership)

    def test_can_delete_membership_if_is_admin_and_is_own_membership(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        membership = Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert user.has_perm("communities.delete_membership", membership)
