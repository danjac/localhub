# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Membership
from communikit.events.tests.factories import EventFactory
from communikit.likes.models import Like
from communikit.posts.tests.factories import PostFactory
from communikit.subscriptions.models import Subscription
from communikit.users.tests.factories import UserFactory

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
        assert len(response.context["object_list"]) == 1
        assert response.context["num_likes"] == 1


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
        assert len(response.context["object_list"]) == 2
        assert response.context["num_likes"] == 1


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
        assert response.url == login_user.get_absolute_url()
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


class TestUserSubscribeView:
    def test_post(self, client: Client, member: Membership):
        user = UserFactory()
        Membership.objects.create(member=user, community=member.community)
        response = client.post(
            reverse("users:subscribe", args=[user.username])
        )
        assert response.url == user.get_absolute_url()
        sub = Subscription.objects.get()
        assert sub.content_object == user
        assert sub.subscriber == member.member
        assert sub.community == member.community

    def test_post_if_user_same_as_auth_user(
        self, client: Client, member: Membership
    ):
        response = client.post(
            reverse("users:subscribe", args=[member.member.username])
        )
        assert response.status_code == 404
        assert not Subscription.objects.exists()


class TestUserUnsubscribeView:
    def test_post(self, client: Client, member: Membership):
        user = UserFactory()
        Membership.objects.create(member=user, community=member.community)
        Subscription.objects.create(
            content_object=user,
            subscriber=member.member,
            community=member.community,
        )
        response = client.post(
            reverse("users:unsubscribe", args=[user.username])
        )
        assert response.url == user.get_absolute_url()
        assert not Subscription.objects.exists()


class TestUserListView:
    def test_get(
        self,
        client: Client,
        member: Membership,
        user: settings.AUTH_USER_MODEL,
    ):
        Membership.objects.create(member=user, community=member.community)
        response = client.get(reverse("users:list"))
        assert len(response.context["object_list"]) == 2


class TestUserAutocompleteListView:
    def test_get(
        self,
        client: Client,
        member: Membership,
        user: settings.AUTH_USER_MODEL,
    ):
        Membership.objects.create(member=user, community=member.community)
        response = client.get(
            reverse("users:autocomplete_list"), {"q": user.username}
        )
        assert len(response.context["object_list"]) == 1
