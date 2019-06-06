# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Membership
from communikit.events.tests.factories import EventFactory
from communikit.notifications.models import Notification
from communikit.photos.tests.factories import PhotoFactory
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestNotificationListView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        comment = CommentFactory(activity=post)
        Notification.objects.create(
            content_object=comment,
            recipient=member.member,
            actor=comment.owner,
            community=post.community,
            verb="created",
        )
        event = EventFactory(community=member.community)
        Notification.objects.create(
            content_object=event,
            recipient=member.member,
            actor=event.owner,
            community=event.community,
            verb="created",
        )
        photo = PhotoFactory(community=member.community)
        Notification.objects.create(
            content_object=event,
            recipient=member.member,
            actor=photo.owner,
            community=photo.community,
            verb="created",
        )
        response = client.get(reverse("notifications:list"))
        assert len(response.context["object_list"]) == 3
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
            reverse(
                "notifications:mark_notification_read", args=[notification.id]
            )
        )
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read
