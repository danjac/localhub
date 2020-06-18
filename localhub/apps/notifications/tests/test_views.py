# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import json

# Django
from django.urls import reverse

# Third Party Libraries
import pytest

# Localhub
# Social-BFG
from localhub.apps.comments.factories import CommentFactory
from localhub.apps.communities.factories import MembershipFactory
from localhub.apps.events.factories import EventFactory
from localhub.apps.photos.factories import PhotoFactory
from localhub.apps.posts.factories import PostFactory

# Local
from ..factories import NotificationFactory
from ..models import Notification, PushSubscription

pytestmark = pytest.mark.django_db


class TestNotificationListView:
    def test_get(self, client, member):
        owner = MembershipFactory(community=member.community).member
        post = PostFactory(community=member.community, owner=owner)
        NotificationFactory(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="followed_user",
        )
        comment = CommentFactory(content_object=post, owner=owner)
        NotificationFactory(
            content_object=comment,
            recipient=member.member,
            actor=comment.owner,
            community=post.community,
            verb="new_comment",
        )
        event = EventFactory(community=member.community, owner=owner)
        NotificationFactory(
            content_object=event,
            recipient=member.member,
            actor=event.owner,
            community=event.community,
            verb="followed_user",
        )
        photo = PhotoFactory(community=member.community, owner=owner)
        NotificationFactory(
            content_object=photo,
            recipient=member.member,
            actor=photo.owner,
            community=photo.community,
            verb="followed_user",
        )
        response = client.get(reverse("notifications:list"))
        assert len(response.context["object_list"]) == 4
        assert response.status_code == 200


class TestNotificationMarkReadView:
    def test_post(self, client, member, mocker):
        owner = MembershipFactory(community=member.community).member
        post = PostFactory(community=member.community, owner=owner)
        notification = NotificationFactory(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
        )

        mock_notification_read = mocker.patch(
            "localhub.apps.notifications.signals.notification_read"
        )

        response = client.post(
            reverse("notifications:mark_read", args=[notification.id])
        )
        assert mock_notification_read.send.called_with(instance=post)
        assert response.status_code == 204
        notification.refresh_from_db()
        assert notification.is_read


class TestNotificationMarkReadRedirectView:
    def test_post(self, client, member, mocker):
        owner = MembershipFactory(community=member.community).member
        post = PostFactory(community=member.community, owner=owner)
        notification = NotificationFactory(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
        )

        mock_notification_read = mocker.patch(
            "localhub.apps.notifications.signals.notification_read"
        )

        response = client.post(
            reverse("notifications:mark_read_redirect", args=[notification.id])
        )
        assert mock_notification_read.send.called_with(instance=post)
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read


class TestNotificationMarkAllReadView:
    def test_post(self, client, member, mocker):
        owner = MembershipFactory(community=member.community).member
        post = PostFactory(community=member.community, owner=owner)
        notification = NotificationFactory(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        mock_notification_read = mocker.patch(
            "localhub.apps.notifications.signals.notification_read"
        )

        response = client.post(
            reverse("notifications:mark_read", args=[notification.id])
        )
        response = client.post(reverse("notifications:mark_all_read"))
        assert mock_notification_read.send.called_with(instance=post)
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read


class TestNotificationDeleteView:
    def test_post(self, client, member):
        owner = MembershipFactory(community=member.community).member
        post = PostFactory(community=member.community, owner=owner)
        notification = NotificationFactory(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
        )
        response = client.post(reverse("notifications:delete", args=[notification.id]))
        assert response.url == reverse("notifications:list")
        assert not Notification.objects.exists()


class TestNotificationDeleteAllView:
    def test_delete(self, client, member):
        owner = MembershipFactory(community=member.community).member
        post = PostFactory(community=member.community, owner=owner)
        NotificationFactory(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
        )
        response = client.delete(reverse("notifications:delete_all"))
        assert response.url == reverse("notifications:list")
        assert not Notification.objects.exists()


class TestSubscribeView:
    def test_post_if_keys_missing(self, client, member):
        body = {"endpoint": "http://xyz"}
        response = client.post(
            reverse("notifications:subscribe"),
            json.dumps(body),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert not PushSubscription.objects.exists()

    def test_post(self, client, member):
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
        assert sub.user == member.member
        assert sub.community == member.community
        assert sub.endpoint == "http://xyz"
        assert sub.auth == "auth"
        assert sub.p256dh == "xxxx"


class TestUnsubscribeView:
    def test_post_if_keys_missing(self, client, member):
        body = {"endpoint": "http://xyz"}
        response = client.post(
            reverse("notifications:unsubscribe"),
            json.dumps(body),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_post(self, client, member):
        PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz",
            auth="auth",
            p256dh="xxxx",
        )
        body = {
            "endpoint": "http://xyz",
            "keys": {"auth": "auth", "p256dh": "xxxx"},
        }
        response = client.post(
            reverse("notifications:unsubscribe"),
            json.dumps(body),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert not PushSubscription.objects.exists()


class TestServiceWorkerView:
    def test_get(self, client, login_user):
        response = client.get(reverse("notifications:service_worker"))
        assert response.status_code == 200
        assert response["Content-Type"] == "application/javascript"
