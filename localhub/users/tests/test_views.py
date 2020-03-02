# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from localhub.comments.factories import CommentFactory
from localhub.communities.factories import MembershipFactory
from localhub.events.factories import EventFactory
from localhub.likes.models import Like
from localhub.notifications.factories import NotificationFactory
from localhub.notifications.models import Notification
from localhub.posts.factories import PostFactory
from localhub.private_messages.factories import MessageFactory

from ..factories import UserFactory

pytestmark = pytest.mark.django_db


User = get_user_model()


class TestMemberListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        response = client.get(reverse("users:member_list"))
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert user in object_list
        assert member.member in object_list


class TestFollowingUserListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.following.add(user)
        response = client.get(reverse("users:following_list"))
        assert response.status_code == 200
        assert response.context["object_list"][0] == user


class TestBlockedUserListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.blocked.add(user)
        response = client.get(reverse("users:blocked_list"))
        assert response.status_code == 200
        assert response.context["object_list"][0] == user


class TestFollowerUserListView:
    def test_get(self, client, member):
        user = MembershipFactory(community=member.community).member
        user.following.add(member.member)
        response = client.get(reverse("users:follower_list"))
        assert response.status_code == 200
        assert response.context["object_list"][0] == user


class TestUserCommentsView:
    def test_get(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post, owner=member.member, community=member.community,
        )
        Like.objects.create(
            content_object=comment,
            user=UserFactory(),
            community=comment.community,
            recipient=comment.owner,
        )
        response = client.get(reverse("users:comments", args=[comment.owner.username]))
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 1
        assert dict(response.context or {})["num_likes"] == 1


class TestUserActivitiesView:
    def test_get_if_current_user(self, client, member):

        post = PostFactory(community=member.community, owner=member.member)
        EventFactory(community=member.community, owner=member.member)
        # unlikely, but just for testing
        notification = NotificationFactory(
            recipient=member.member, content_object=member.member, is_read=False
        )
        Like.objects.create(
            user=UserFactory(),
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )

        response = client.get(
            reverse("users:activities", args=[member.member.username])
        )
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 2
        assert dict(response.context or {})["num_likes"] == 1

        # ignore: user is self
        notification.refresh_from_db()
        assert not notification.is_read

    def test_get_if_other_user(self, client, member):

        other = MembershipFactory(community=member.community)
        post = PostFactory(community=member.community, owner=other.member)
        EventFactory(community=member.community, owner=other.member)
        notification = NotificationFactory(
            recipient=member.member, content_object=other.member, is_read=False
        )
        Like.objects.create(
            user=UserFactory(),
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )

        response = client.get(reverse("users:activities", args=[other.member.username]))
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 2
        assert dict(response.context or {})["num_likes"] == 1

        notification.refresh_from_db()
        assert notification.is_read

    def test_get_if_other_user_email_same_as_username(self, client, member):
        """
        Test for regex
        """
        other = MembershipFactory(
            community=member.community, member=UserFactory(username="tester@gmail.com")
        )
        response = client.get(reverse("users:activities", args=[other.member.username]))
        assert response.status_code == 200


class TestUserUpdateView:
    def test_get(self, client, login_user):
        response = client.get(reverse("user_update"))
        assert response.status_code == 200

    def test_post(self, client, login_user):
        response = client.post(
            reverse("user_update"),
            {"name": "New Name", "language": "en", "default_timezone": "UTC"},
        )
        assert response.url == reverse("user_update")
        login_user.refresh_from_db()
        assert login_user.name == "New Name"


class TestUserDeleteView:
    def test_get(self, client, login_user):
        response = client.get(reverse("user_delete"))
        assert response.status_code == 200

    def test_post(self, client, login_user):
        response = client.post(reverse("user_delete"))
        assert response.url == "/"
        assert User.objects.filter(username=login_user.username).count() == 0


class TestUserFollowView:
    def test_post(self, client, member, mailoutbox, send_notification_webpush_mock):
        user = MembershipFactory(
            community=member.community,
            member=UserFactory(notification_preferences=["new_follower"]),
        ).member
        response = client.post(reverse("users:follow", args=[user.username]))
        assert response.url == user.get_absolute_url()
        assert user in member.member.following.all()
        notification = Notification.objects.get()
        assert notification.recipient == user
        assert notification.content_object == member.member
        assert notification.actor == member.member
        assert mailoutbox[0].to == [user.email]


class TestUserBlockView:
    def test_post(self, client, member):
        user = MembershipFactory(community=member.community).member
        response = client.post(reverse("users:block", args=[user.username]))
        assert response.url == user.get_absolute_url()
        assert user in member.member.blocked.all()


class TestUserUnfollowView:
    def test_post(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.following.add(user)
        response = client.post(reverse("users:unfollow", args=[user.username]))
        assert response.url == user.get_absolute_url()
        assert user not in member.member.following.all()


class TestUserUnblockView:
    def test_post(self, client, member):
        user = MembershipFactory(community=member.community).member
        member.member.blocked.add(user)
        response = client.post(reverse("users:unblock", args=[user.username]))
        assert user not in member.member.blocked.all()
        assert response.url == user.get_absolute_url()


class TestUserAutocompleteListView:
    def test_get(self, client, member, user):
        other = MembershipFactory(
            community=member.community, member=UserFactory(name="tester")
        ).member

        blocker = MembershipFactory(
            community=member.community, member=UserFactory(name="tester")
        ).member

        blocker.blocked.add(member.member)

        response = client.get(reverse("users:autocomplete_list"), {"q": "tester"})
        object_list = response.context["object_list"]
        assert other in object_list
        assert blocker not in object_list


class TestUserMessageListView:
    def test_get_if_other(self, client, member):
        other_user = MembershipFactory(community=member.community).member
        from_me = MessageFactory(
            community=member.community, sender=member.member, recipient=other_user,
        )
        to_me = MessageFactory(
            community=member.community, sender=other_user, recipient=member.member,
        )
        to_someone_else = MessageFactory(community=member.community, sender=other_user)
        response = client.get(reverse("users:messages", args=[other_user.username]))
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert from_me in object_list
        assert to_me in object_list
        assert to_someone_else not in object_list

    def test_get_if_current_user(self, client, member):
        other_user = MembershipFactory(community=member.community).member
        from_me = MessageFactory(
            community=member.community, sender=member.member, recipient=other_user,
        )
        to_me = MessageFactory(
            community=member.community, sender=other_user, recipient=member.member,
        )
        to_someone_else = MessageFactory(community=member.community, sender=other_user)
        response = client.get(reverse("users:messages", args=[member.member.username]))
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert from_me in object_list
        assert to_me in object_list
        assert to_someone_else not in object_list


class TestDarkmodeToggleView:
    def test_post_if_lightmode(self, client):
        response = client.post(reverse("darkmode_toggle"))
        assert response.status_code == 200
        assert response.cookies["darkmode"].value == "true"

    def test_post_if_darkmode(self, client):
        client.cookies["darkmode"] = "1"
        response = client.post(reverse("darkmode_toggle"))
        assert response.status_code == 200
        assert response.cookies["darkmode"].value == ""
