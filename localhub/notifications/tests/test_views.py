# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Membership
from localhub.events.tests.factories import EventFactory
from localhub.notifications.models import Notification, PushSubscription
from localhub.photos.tests.factories import PhotoFactory
from localhub.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestNotificationListView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="new_followed_user_post",
        )
        comment = CommentFactory(content_object=post)
        Notification.objects.create(
            content_object=comment,
            recipient=member.member,
            actor=comment.owner,
            community=post.community,
            verb="new_comment",
        )
        event = EventFactory(community=member.community)
        Notification.objects.create(
            content_object=event,
            recipient=member.member,
            actor=event.owner,
            community=event.community,
            verb="new_followed_user_post",
        )
        photo = PhotoFactory(community=member.community)
        Notification.objects.create(
            content_object=photo,
            recipient=member.member,
            actor=photo.owner,
            community=photo.community,
            verb="new_followed_user_post",
        )
        response = client.get(reverse("notifications:list"))
        assert len(response.context["object_list"]) == 4
        assert response.status_code == 200


class TestNotificationMarkReadView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        notification = Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        response = client.post(
            reverse("notifications:mark_read", args=[notification.id])
        )
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read


class TestNotificationMarkAllReadView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        notification = Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        response = client.post(reverse("notifications:mark_all_read"))
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read


class TestNotificationDeleteView:
    def test_delete(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        notification = Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        response = client.delete(
            reverse("notifications:delete", args=[notification.id])
        )
        assert response.url == reverse("notifications:list")
        assert not Notification.objects.exists()


class TestNotificationDeleteAllView:
    def test_delete(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        response = client.delete(reverse("notifications:delete_all"))
        assert response.url == reverse("notifications:list")
        assert not Notification.objects.exists()


class TestSubscribeView:
    def test_post_if_keys_missing(
        self, client: Client, login_user: settings.AUTH_USER_MODEL
    ):
        body = {"endpoint": "http://xyz"}
        response = client.post(
            reverse("notifications:subscribe"),
            json.dumps(body),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert not PushSubscription.objects.exists()

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        body = {
            "endpoint": "http://xyz",
            "keys": {"auth": "auth", "p256dh": "xxxx"},
        }
        response = client.post(
            reverse("notifications:subscribe"),
            json.dumps(body),
            content_type="application/json",
        )
        assert response.status_code == 201

        sub = PushSubscription.objects.get()
        assert sub.user == login_user
        assert sub.endpoint == "http://xyz"
        assert sub.auth == "auth"
        assert sub.p256dh == "xxxx"


class TestServiceWorkerView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get(reverse("notifications:service_worker"))
        assert response.status_code == 200
        assert response["Content-Type"] == "application/javascript"
