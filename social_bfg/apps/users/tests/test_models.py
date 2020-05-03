# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone

import pytest
from allauth.account.models import EmailAddress
from social_bfg.apps.communities.factories import CommunityFactory, MembershipFactory
from social_bfg.apps.communities.models import Membership
from social_bfg.apps.private_messages.factories import MessageFactory

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

    def test_with_joined(self, user_model, member):
        first = user_model.objects.with_joined(member.community).first()
        assert first.joined is not None

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
        MessageFactory(recipient=member.member, community=member.community)
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert user.num_unread_messages == 1

    def test_with_num_unread_messages_if_recipient_unread_other_community(
        self, user_model, member
    ):
        MessageFactory(recipient=member.member)
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_no_messages(self, user_model, member):
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert not hasattr(user, "num_unread_messages")

    def test_with_num_unread_messages_if_sender_unread(self, user_model, member):
        MessageFactory(sender=member.member, community=member.community)
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_recipient_read(self, user_model, member):
        MessageFactory(
            recipient=member.member, community=member.community, read=timezone.now(),
        )
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_recipient_deleted(self, user_model, member):
        MessageFactory(
            recipient=member.member,
            community=member.community,
            recipient_deleted=timezone.now(),
        )
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_with_num_unread_messages_if_sender_deleted(self, user_model, member):
        MessageFactory(
            recipient=member.member,
            community=member.community,
            sender_deleted=timezone.now(),
        )
        user = (
            user_model.objects.exclude(pk=member.member_id)
            .with_num_unread_messages(member.member, member.community)
            .first()
        )
        assert user.num_unread_messages == 0

    def test_exclude_blocked(self, user_model, user):
        other = UserFactory()
        user.blocked.add(other)
        assert user_model.objects.exclude_blocked(user).exclude(pk=user.pk).count() == 0

    def test_exclude_blockers(self, user_model, user):
        other = UserFactory()
        other.blocked.add(user)
        assert (
            user_model.objects.exclude_blockers(user).exclude(pk=user.pk).count() == 0
        )

    def test_exclude_blocking(self, user_model, user):
        first = UserFactory()
        second = UserFactory()
        third = UserFactory()

        user.blockers.add(first)
        second.blockers.add(user)
        users = user_model.objects.exclude_blocking(user).exclude(pk=user.pk)
        assert users.count() == 1
        assert users.first() == third


class TestUserModel:
    def test_has_tracker_changed(self, user):

        user.reset_tracker()
        assert not user.has_tracker_changed()
        user.bio = "new bio!"
        assert user.has_tracker_changed()
        # ensure it still appears changed after save
        user.save()
        assert user.has_tracker_changed()
        # refresh from db should reset...
        user.refresh_from_db()
        assert not user.has_tracker_changed()

    def test_get_email_addresses(self, user):

        user.emailaddress_set.create(email="test1@gmail.com")
        emails = user.get_email_addresses()
        assert user.email in emails
        assert "test1@gmail.com" in emails

    def test_is_active_member_if_true(self):
        member = MembershipFactory(active=True)
        assert member.member.is_active_member(member.community)

    def test_is_active_member_if_false(self):
        member = MembershipFactory(active=False)
        assert not member.member.is_active_member(member.community)

    def test_is_inactive_member_if_true(self):
        member = MembershipFactory(active=False)
        assert member.member.is_inactive_member(member.community)

    def test_is_inactive_member_if_false(self):
        member = MembershipFactory(active=True)
        assert not member.member.is_inactive_member(member.community)

    def test_has_role_if_not_a_member(self, user, community):
        assert not user.has_role(community, Membership.Role.MEMBER)

    def test_has_role_if_active_member_wrong_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.MEMBER)
        assert not member.member.has_role(member.community, Membership.Role.ADMIN)

    def test_has_role_if_inactive_member_right_role(self):
        member = MembershipFactory(active=False, role=Membership.Role.ADMIN)
        assert not member.member.has_role(member.community, Membership.Role.ADMIN)

    def test_has_role_if_active_member_right_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.ADMIN)
        assert member.member.has_role(member.community, Membership.Role.ADMIN)

    def test_is_member_if_not_a_member(self, user, community):
        assert not user.is_member(community)

    def test_is_member_if_active_member_wrong_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.ADMIN)
        assert not member.member.is_member(member.community)

    def test_is_member_if_inactive_member_right_role(self):
        member = MembershipFactory(active=False, role=Membership.Role.MEMBER)
        assert not member.member.is_member(member.community)

    def test_is_member_if_active_member_right_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.MEMBER)
        assert member.member.is_member(member.community)

    def test_is_moderator_if_not_a_member(self, user, community):
        assert not user.is_moderator(community)

    def test_is_moderator_if_active_member_wrong_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.ADMIN)
        assert not member.member.is_moderator(member.community)

    def test_is_moderator_if_inactive_member_right_role(self):
        member = MembershipFactory(active=False, role=Membership.Role.MODERATOR)
        assert not member.member.is_moderator(member.community)

    def test_is_moderator_if_active_member_right_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.MODERATOR)
        assert member.member.is_moderator(member.community)

    def test_is_admin_if_active_member_wrong_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.MEMBER)
        assert not member.member.is_admin(member.community)

    def test_is_admin_if_inactive_member_right_role(self):
        member = MembershipFactory(active=False, role=Membership.Role.ADMIN)
        assert not member.member.is_admin(member.community)

    def test_is_admin_if_active_member_right_role(self):
        member = MembershipFactory(active=True, role=Membership.Role.ADMIN)
        assert member.member.is_admin(member.community)

    def test_member_cache(self):

        user = UserFactory()

        first = MembershipFactory(
            member=user, role=Membership.Role.ADMIN, active=True
        ).community
        second = MembershipFactory(
            member=user, role=Membership.Role.MODERATOR, active=True
        ).community
        third = MembershipFactory(
            member=user, role=Membership.Role.MEMBER, active=True
        ).community
        fourth = MembershipFactory(
            member=user, role=Membership.Role.MEMBER, active=False
        ).community
        fifth = CommunityFactory()

        assert user.member_cache.has_role(first.id, [Membership.Role.ADMIN])
        assert user.member_cache.has_role(second.id, [Membership.Role.MODERATOR])
        assert user.member_cache.has_role(third.id, [Membership.Role.MEMBER])

        assert user.member_cache.has_role(first.id)
        assert user.member_cache.has_role(second.id)
        assert user.member_cache.has_role(third.id)

        assert not user.member_cache.has_role(fourth.id)
        assert not user.member_cache.has_role(fifth.id)

        assert not user.member_cache.is_inactive(first.id)
        assert not user.member_cache.is_inactive(second.id)
        assert not user.member_cache.is_inactive(third.id)
        assert not user.member_cache.is_inactive(fifth.id)
        assert user.member_cache.is_inactive(fourth.id)

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

    def test_get_display_name_if_no_name(self, user_model):
        assert user_model(username="danjac").get_display_name() == "danjac"

    def test_get_display_name_if_name(self, user_model):
        assert (
            user_model(username="danjac", name="Dan Jacob").get_display_name()
            == "Dan Jacob"
        )

    def test_get_initials(self, user_model):
        assert user_model(username="danjac", name="Dan Jacob").get_initials() == "DJ"

    def test_has_role(self, moderator):
        assert moderator.member.has_role(moderator.community, Membership.Role.MODERATOR)

    def test_does_not_have_role(self, member):
        assert not member.member.has_role(member.community, Membership.Role.MODERATOR)

    def test_notify_on_update(self, member, send_webpush_mock):

        follower = MembershipFactory(community=member.community)
        other_community_follower = MembershipFactory()
        non_member_follower = UserFactory()

        member.member.followers.add(follower.member)
        member.member.followers.add(other_community_follower.member)
        member.member.followers.add(non_member_follower)

        MembershipFactory(
            member=member.member, community=other_community_follower.community
        )

        # add first follower to same community: should just be one update !

        MembershipFactory(
            member=follower.member, community=other_community_follower.community,
        )

        member.member.reset_tracker()

        # no change to notifiable user settings
        notifications = member.member.notify_on_update()
        assert len(notifications) == 0

        # trigger update by changing bio...
        member.member.bio = "testme"
        member.member.save()

        notifications = member.member.notify_on_update()

        assert len(notifications) == 2
        assert notifications[0].actor == member.member
        assert notifications[0].verb == "update"

        recipients = [n.recipient for n in notifications]
        assert follower.member in recipients
        assert other_community_follower.member in recipients

        assert send_webpush_mock.is_called()

    def test_notify_on_join(self, member, send_webpush_mock):
        other_member = MembershipFactory(community=member.community,).member
        notifications = member.member.notify_on_join(member.community)
        assert len(notifications) == 1
        assert notifications[0].recipient == other_member
        assert notifications[0].content_object == member.member
        assert notifications[0].actor == member.member
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_member"
        assert send_webpush_mock.is_called()

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
        assert send_webpush_mock.is_called()

    def test_dismiss_notice(self, user):
        user.dismiss_notice("private-stash")
        user.refresh_from_db()
        assert "private-stash" in user.dismissed_notices

    def test_block_user(self, user):
        other = UserFactory()
        user.block_user(other)
        assert other in user.blocked.all()

    def test_block_user_if_following(self, user):
        other = UserFactory()
        user.following.add(other)
        user.block_user(other)
        assert other in user.blocked.all()
        assert other not in user.following.all()

    def test_block_user_if_follower(self, user):
        other = UserFactory()
        other.following.add(user)
        user.block_user(other)
        assert other in user.blocked.all()
        assert other not in user.followers.all()
