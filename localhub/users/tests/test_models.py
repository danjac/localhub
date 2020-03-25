# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from allauth.account.models import EmailAddress
from django.utils import timezone

from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.private_messages.factories import MessageFactory

from ..factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self, user_model):

        user = user_model.objects.create_user(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.check_password("t3ZtP4s31")

    def test_active_for_community(self, user_model, community):
        Membership.objects.create(member=UserFactory(), community=community)
        assert user_model.objects.for_community(community).exists()

    def test_active_for_community_if_not_member(self, user_model, community):
        UserFactory()
        assert not user_model.objects.for_community(community).exists()

    def test_active_for_community_if_not_active_member(self, user_model, community):
        Membership.objects.create(
            member=UserFactory(), community=community, active=False
        )
        assert not user_model.objects.for_community(community).exists()

    def test_inactive_for_community(self, user_model, community):
        Membership.objects.create(
            member=UserFactory(is_active=False), community=community
        )
        assert not user_model.objects.for_community(community).exists()

    def test_with_role_if_not_member(self, user_model, community):
        UserFactory()
        first = user_model.objects.with_role(community).first()
        assert first.role is None
        assert first.role_display == ""

    def test_with_role_if_member(self, user_model, community):
        MembershipFactory(community=community, role="member")
        first = user_model.objects.with_role(community).first()
        assert first.role == "member"
        assert first.role_display == "Member"

    def test_with_role_if_moderator(self, user_model, community):
        MembershipFactory(community=community, role="moderator")
        first = user_model.objects.with_role(community).first()
        assert first.role == "moderator"
        assert first.role_display == "Moderator"

    def test_with_role_if_admin(self, user_model, community):
        MembershipFactory(community=community, role="admin")
        first = user_model.objects.with_role(community).first()
        assert first.role == "admin"
        assert first.role_display == "Admin"

    def test_create_superuser(self, user_model):

        user = user_model.objects.create_superuser(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.is_superuser
        assert user.is_staff

    def test_for_email_matching_email_field(self, user_model):

        user = UserFactory(email="test@gmail.com")
        assert user_model.objects.for_email("test@gmail.com").first() == user

    def test_for_email_matching_email_address_instance(self, user_model):

        user = UserFactory()
        EmailAddress.objects.create(user=user, email="test@gmail.com")
        assert user_model.objects.for_email("test@gmail.com").first() == user

    def test_matches_usernames(self, user_model):
        user_1 = UserFactory(username="first")
        user_2 = UserFactory(username="second")
        user_3 = UserFactory(username="third")

        names = ["second", "FIRST", "SEconD"]  # duplicate

        users = user_model.objects.matches_usernames(names)
        assert len(users) == 2
        assert user_1 in users
        assert user_2 in users
        assert user_3 not in users

        # check empty set returns no results
        assert user_model.objects.matches_usernames([]).count() == 0

    def test_is_following(self, user_model, user):

        followed = UserFactory()
        UserFactory()

        user.following.add(followed)

        users = user_model.objects.all().with_is_following(user)

        for user in users:
            if user == followed:
                assert user.is_following
            else:
                assert not user.is_following

    def test_is_blocked(self, user_model, user):

        blocked = UserFactory()
        UserFactory()

        user.blocked.add(blocked)

        users = user_model.objects.all().with_is_blocked(user)

        for user in users:
            if user == blocked:
                assert user.is_blocked
            else:
                assert not user.is_blocked

    def test_with_num_unread_messages_if_recipient_unread(self, user_model, member):
        MessageFactory(recipient=member.member)
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member)
            .first()
        )
        assert user.num_unread_messages == 1

    def test_with_num_unread_messages_if_no_messages(self, user_model, member):
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member)
            .first()
        )
        assert not hasattr(user, "num_unread_messages")

    def test_with_num_unread_messages_if_sender_unread(self, user_model, member):
        MessageFactory(sender=member.member)
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_recipient_read(self, user_model, member):
        MessageFactory(recipient=member.member, read=timezone.now())
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_recipient_deleted(self, user_model, member):
        MessageFactory(recipient=member.member, recipient_deleted=timezone.now())
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_sender_deleted(self, user_model, member):
        MessageFactory(recipient=member.member, sender_deleted=timezone.now())
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member)
            .first()
        )
        assert user.num_unread_messages == 0


class TestUserModel:
    def test_get_email_addresses(self, user):

        user.emailaddress_set.create(email="test1@gmail.com")
        emails = user.get_email_addresses()
        assert user.email in emails
        assert "test1@gmail.com" in emails

    def test_get_blocked_users(self, user):
        blocked = UserFactory()
        blocker = UserFactory()
        not_blocked = UserFactory()

        user.blocked.add(blocked)
        user.blockers.add(blocker)

        users = user.get_blocked_users()
        assert blocked in users
        assert blocker in users
        assert not_blocked not in users

    def test_is_blocked(self, user):
        blocked = UserFactory()
        blocker = UserFactory()
        not_blocked = UserFactory()

        user.blocked.add(blocked)
        user.blockers.add(blocker)

        assert user.is_blocked(blocked)
        assert user.is_blocked(blocker)
        assert not user.is_blocked(not_blocked)
        assert not user.is_blocked(user)

    def test_get_absolute_url(self, user):
        assert user.get_absolute_url() == f"/people/{user.username}/"

    def test_has_role(self, moderator):
        assert moderator.member.has_role(moderator.community, Membership.Role.MODERATOR)

    def test_does_not_have_role(self, member):
        assert not member.member.has_role(member.community, Membership.Role.MODERATOR)

    def test_notify_on_join(self, member, send_webpush_mock):
        other_member = MembershipFactory(
            community=member.community, member=UserFactory(),
        ).member
        notifications = member.member.notify_on_join(member.community)
        assert len(notifications) == 1
        assert notifications[0].recipient == other_member
        assert notifications[0].content_object == member.member
        assert notifications[0].actor == member.member
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_member"

    def test_notify_on_follow(self, member, send_webpush_mock):
        follower = MembershipFactory(
            community=member.community, member=UserFactory(),
        ).member
        notifications = follower.notify_on_follow(member.member, member.community)
        assert len(notifications) == 1
        assert notifications[0].recipient == member.member
        assert notifications[0].content_object == follower
        assert notifications[0].actor == follower
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_follower"
