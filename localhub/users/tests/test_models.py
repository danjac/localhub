# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory

from allauth.account.models import EmailAddress

from localhub.communities.models import Community, Membership, RequestCommunity
from localhub.messageboard.tests.factories import MessageRecipientFactory
from localhub.notifications.models import Notification
from localhub.subscriptions.models import Subscription
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self):

        user = get_user_model().objects.create_user(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.check_password("t3ZtP4s31")

    def test_active(self, community: Community):
        Membership.objects.create(member=UserFactory(), community=community)
        assert get_user_model().objects.active(community).exists()

    def test_active_if_not_member(self, community: Community):
        UserFactory()
        assert not get_user_model().objects.active(community).exists()

    def test_active_if_not_active_member(self, community: Community):
        Membership.objects.create(
            member=UserFactory(), community=community, active=False
        )
        assert not get_user_model().objects.active(community).exists()

    def test_active_if_not_active(self, community: Community):
        Membership.objects.create(
            member=UserFactory(is_active=False), community=community
        )
        assert not get_user_model().objects.active(community).exists()

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

    def test_has_subscribed(self, member: Membership):

        subscribed = UserFactory()
        UserFactory()

        Subscription.objects.create(
            subscriber=member.member,
            community=member.community,
            content_object=subscribed,
        )

        users = (
            get_user_model()
            .objects.all()
            .with_has_subscribed(member.member, member.community)
        )

        for user in users:
            if user == subscribed:
                assert user.has_subscribed
            else:
                assert not user.has_subscribed


class TestUserModel:
    def test_get_absolute_url(self, user: settings.AUTH_USER_MODEL):
        assert user.get_absolute_url() == f"/people/{user.username}/"

    def test_has_email_pref(self):
        user = UserFactory(email_preferences=["messages"])
        assert user.has_email_pref("messages")

    def test_does_not_have_email_pref(self):
        user = UserFactory()
        assert not user.has_email_pref("messages")

    def test_has_role(self, moderator: Membership):
        assert moderator.member.has_role(
            moderator.community, Membership.ROLES.moderator
        )

    def test_does_not_have_role(self, member: Membership):
        assert not member.member.has_role(
            member.community, Membership.ROLES.moderator
        )

    def test_get_unread_notification_count(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        Notification.objects.create(
            verb="mention",
            recipient=user,
            community=community,
            content_object=PostFactory(),
            actor=UserFactory(),
        )
        assert user.get_unread_notification_count(community) == 1

    def test_get_unread_notification_count_if_community_id_none(
        self, user: settings.AUTH_USER_MODEL, req_factory: RequestFactory
    ):
        req = req_factory.get("/")
        assert user.get_unread_notification_count(RequestCommunity(req)) == 0

    def test_get_unread_message_count(self):
        recipient = MessageRecipientFactory()
        assert (
            recipient.recipient.get_unread_message_count(
                recipient.message.community
            )
            == 1
        )

    def test_get_unread_message_count_if_community_id_none(
        self, user: settings.AUTH_USER_MODEL, req_factory: RequestFactory
    ):
        req = req_factory.get("/")
        assert user.get_unread_message_count(RequestCommunity(req)) == 0
