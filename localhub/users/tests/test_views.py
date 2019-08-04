# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.events.tests.factories import EventFactory
from localhub.likes.models import Like
from localhub.notifications.models import Notification
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


User = get_user_model()


class TestUserCommentsView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post,
            owner=member.member,
            community=member.community,
        )
        Like.objects.create(
            content_object=comment,
            user=UserFactory(),
            community=comment.community,
            recipient=comment.owner,
        )
        response = client.get(
            reverse("users:comments", args=[comment.owner.username])
        )
        assert response.status_code == 200
        assert len(dict(response.context or {})["object_list"]) == 1
        assert dict(response.context or {})["num_likes"] == 1


class TestUserActivitiesView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community, owner=member.member)
        EventFactory(community=member.community, owner=member.member)

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


class TestUserDetailView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(
            reverse("users:detail", args=[member.member.username])
        )
        assert response.status_code == 200


class TestUserUpdateView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get(reverse("user_update"))
        assert response.status_code == 200

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.post(reverse("user_update"), {"name": "New Name"})
        assert response.url == reverse("user_update")
        login_user.refresh_from_db()
        assert login_user.name == "New Name"


class TestUserDeleteView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get(reverse("user_delete"))
        assert response.status_code == 200

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.post(reverse("user_delete"))
        assert response.url == "/"
        assert User.objects.filter(username=login_user.username).count() == 0


class TestUserFollowView:
    def test_post(self, client: Client, member: Membership):
        user = MembershipFactory(community=member.community).member
        response = client.post(reverse("users:follow", args=[user.username]))
        assert response.url == user.get_absolute_url()
        assert user in member.member.following.all()
        notification = Notification.objects.get()
        assert notification.recipient == user
        assert notification.content_object == user
        assert notification.actor == member.member


class TestUserBlockView:
    def test_post(self, client: Client, member: Membership):
        user = MembershipFactory(community=member.community).member
        response = client.post(reverse("users:block", args=[user.username]))
        assert response.url == user.get_absolute_url()
        assert user in member.member.blocked.all()


class TestUserUnfollowView:
    def test_post(self, client: Client, member: Membership):
        user = MembershipFactory(community=member.community).member
        member.member.following.add(user)
        response = client.post(reverse("users:unfollow", args=[user.username]))
        assert user not in member.member.following.all()
        assert response.url == user.get_absolute_url()


class TestUserUnblockView:
    def test_post(self, client: Client, member: Membership):
        user = MembershipFactory(community=member.community).member
        member.member.blocked.add(user)
        response = client.post(reverse("users:unblock", args=[user.username]))
        assert user not in member.member.blocked.all()
        assert response.url == user.get_absolute_url()


class TestUserAutocompleteListView:
    def test_get(
        self,
        client: Client,
        member: Membership,
        user: settings.AUTH_USER_MODEL,
    ):
        other = MembershipFactory(
            community=member.community, member=UserFactory(name="tester")
        ).member
        other.search_indexer.update()

        assert get_user_model().objects.search("tester").get() == other

        blocker = MembershipFactory(
            community=member.community, member=UserFactory(name="tester")
        ).member
        blocker.search_indexer.update()

        blocker.blocked.add(member.member)

        response = client.get(
            reverse("users:autocomplete_list"), {"q": "tester"}
        )
        object_list = response.context["object_list"]
        assert other in object_list
        assert blocker not in object_list
