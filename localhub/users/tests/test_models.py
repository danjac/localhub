# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership

from ..factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self):

        user = get_user_model().objects.create_user(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.check_password("t3ZtP4s31")

    def test_active(self, community):
        Membership.objects.create(member=UserFactory(), community=community)
        assert get_user_model().objects.for_community(community).exists()

    def test_active_if_not_member(self, community):
        UserFactory()
        assert not get_user_model().objects.for_community(community).exists()

    def test_active_if_not_active_member(self, community):
        Membership.objects.create(
            member=UserFactory(), community=community, active=False
        )
        assert not get_user_model().objects.for_community(community).exists()

    def test_active_if_not_active(self, community):
        Membership.objects.create(
            member=UserFactory(is_active=False), community=community
        )
        assert not get_user_model().objects.for_community(community).exists()

    def test_create_superuser(self):

        user = get_user_model().objects.create_superuser(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.is_superuser
        assert user.is_staff

    def test_for_email_matching_email_field(self):

        user = UserFactory(email="test@gmail.com")
        assert get_user_model().objects.for_email("test@gmail.com").first() == user

    def test_for_email_matching_email_address_instance(self):

        user = UserFactory()
        EmailAddress.objects.create(user=user, email="test@gmail.com")
        assert get_user_model().objects.for_email("test@gmail.com").first() == user

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

    def test_is_following(self, user):

        followed = UserFactory()
        UserFactory()

        user.following.add(followed)

        users = get_user_model().objects.all().with_is_following(user)

        for user in users:
            if user == followed:
                assert user.is_following
            else:
                assert not user.is_following

    def test_is_blocked(self, user):

        blocked = UserFactory()
        UserFactory()

        user.blocked.add(blocked)

        users = get_user_model().objects.all().with_is_blocked(user)

        for user in users:
            if user == blocked:
                assert user.is_blocked
            else:
                assert not user.is_blocked


class TestUserModel:
    def test_get_absolute_url(self, user):
        assert user.get_absolute_url() == f"/people/{user.username}/"

    def test_has_notification_pref(self):
        user = UserFactory(notification_preferences=["messages"])
        assert user.has_notification_pref("messages")

    def test_does_not_have_notification_pref(self):
        user = UserFactory()
        assert not user.has_notification_pref("messages")

    def test_has_role(self, moderator):
        assert moderator.member.has_role(
            moderator.community, Membership.ROLES.moderator
        )

    def test_does_not_have_role(self, member):
        assert not member.member.has_role(member.community, Membership.ROLES.moderator)

    def test_notify_on_join(self, member):
        other_member = MembershipFactory(community=member.community, member=UserFactory(notification_preferences=["new_member"])).member
        notifications = member.member.notify_on_join(member.community)
        assert len(notifications) == 1
        assert notifications[0].recipient == other_member
        assert notifications[0].content_object == member.member
        assert notifications[0].actor == member.member
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_member"

    def test_notify_on_follow(self, member):
        follower = MembershipFactory(community=member.community, member=UserFactory(notification_preferences=["new_follower"])).member
        notifications = follower.notify_on_follow(member.member, member.community)
        assert len(notifications) == 1
        assert notifications[0].recipient == member.member
        assert notifications[0].content_object == follower
        assert notifications[0].actor == follower
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_follower"
