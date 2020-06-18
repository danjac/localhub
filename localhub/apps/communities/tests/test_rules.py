# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.apps.users.factories import UserFactory

# Local
from ..factories import MembershipFactory
from ..models import Membership
from ..rules import (
    is_admin,
    is_admin_member,
    is_inactive_member,
    is_member,
    is_moderator,
    is_self,
)

pytestmark = pytest.mark.django_db


class TestMembershipRoles:
    def test_anonymous(self, anonymous_user, community):
        assert not is_member.test(anonymous_user, community)
        assert not is_moderator.test(anonymous_user, community)
        assert not is_admin.test(anonymous_user, community)

    def test_non_member(self, user, community):
        assert not is_member.test(user, community)
        assert not is_moderator.test(user, community)
        assert not is_admin.test(user, community)

    def test_member(self, community):
        user = MembershipFactory(community=community, role="member").member
        assert is_member.test(user, community)
        assert not is_moderator.test(user, community)
        assert not is_admin.test(user, community)
        assert not is_inactive_member.test(user, community)

    def test_moderator(self, community):
        user = MembershipFactory(community=community, role="moderator").member
        assert is_member.test(user, community)
        assert is_moderator.test(user, community)
        assert not is_admin.test(user, community)
        assert not is_inactive_member.test(user, community)

    def test_admin(self, community):
        user = MembershipFactory(community=community, role="admin").member
        assert is_member.test(user, community)
        assert is_moderator.test(user, community)
        assert is_admin.test(user, community)
        assert not is_inactive_member.test(user, community)

    def test_inactive_member(self, community):
        user = MembershipFactory(community=community, active=False).member
        assert not is_member.test(user, community)
        assert is_inactive_member.test(user, community)


class TestIsOwnMembership:
    def test_is_self_if_true(self, user, community):
        membership = Membership.objects.create(
            community=community, member=user, role="admin"
        )
        assert is_self.test(user, membership)

    def test_is_self_if_false(self, user, community):
        membership = Membership.objects.create(
            community=community, member=UserFactory(), role="admin"
        )
        assert not is_self.test(user, membership)


class TestIsMembershipCommunityAdmin:
    def test_is_admin(self, user, community):
        membership = Membership.objects.create(
            community=community, member=user, role="admin"
        )
        assert is_admin_member.test(user, membership)

    def test_is_not_admin(self, user, community):
        membership = Membership.objects.create(
            community=community, member=user, role="member"
        )
        assert not is_admin_member.test(user, membership)


class TestCommunityPermissions:
    def test_can_manage_community_if_user_is_not_admin(self, user, community):
        assert not user.has_perm("communities.manage_community", community)

    def test_can_manage_community_if_user_is_admin(self, user, community):
        Membership.objects.create(member=user, community=community, role="admin")
        assert user.has_perm("communities.manage_community", community)


class TestMembershipPermissions:
    def test_can_change_membership_if_is_admin_and_is_other_membership(
        self, user, community
    ):
        Membership.objects.create(member=user, community=community, role="admin")
        membership = Membership.objects.create(
            member=UserFactory(), community=community, role="admin"
        )
        assert user.has_perm("communities.change_membership", membership)

    def test_can_change_membership_if_is_admin_and_is_self(self, user, community):
        membership = Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert not user.has_perm("communities.change_membership", membership)

    def test_can_delete_membership_if_is_admin_and_is_other_membership(
        self, user, community
    ):
        Membership.objects.create(member=user, community=community, role="admin")
        membership = Membership.objects.create(
            member=UserFactory(), community=community, role="admin"
        )
        assert user.has_perm("communities.delete_membership", membership)

    def test_can_delete_membership_if_not_is_admin_and_is_other_membership(
        self, user, community
    ):
        Membership.objects.create(member=user, community=community, role="member")
        membership = Membership.objects.create(
            member=UserFactory(), community=community, role="admin"
        )
        assert not user.has_perm("communities.delete_membership", membership)

    def test_can_delete_membership_if_not_is_admin_and_is_self(self, user, community):
        membership = Membership.objects.create(
            member=user, community=community, role="member"
        )
        assert user.has_perm("communities.delete_membership", membership)

    def test_can_delete_membership_if_is_admin_and_is_self(self, user, community):
        membership = Membership.objects.create(
            member=user, community=community, role="admin"
        )
        assert user.has_perm("communities.delete_membership", membership)
