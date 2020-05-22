# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils import timezone

# Django Rest Framework
from rest_framework import status

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.apps.bookmarks.models import Bookmark
from social_bfg.apps.comments.factories import CommentFactory
from social_bfg.apps.comments.models import Comment
from social_bfg.apps.likes.models import Like
from social_bfg.apps.notifications.models import Notification

# Local
from ..factories import EventFactory
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventViewSet:
    def test_list_if_member(self, client, member, event):
        response = client.get("/api/events/")
        assert len(response.data["results"]) == 1

    def test_list_if_not_member(self, client, login_user, event):
        response = client.get("/api/events/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_detail(self, client, member, event):
        response = client.get(f"/api/events/{event.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == event.title

    def test_detail_if_not_community_event(self, client, member):
        event = EventFactory()
        response = client.get(f"/api/events/{event.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_and_publish(self, client, member):
        data = {
            "title": "test",
            "description": "test",
            "starts": timezone.now(),
            "timezone": "UTC",
            "publish": "true",
            "allow_comments": "true",
            "url": "",
        }
        response = client.post("/api/events/", data, format="json")
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        event = Event.objects.first()
        assert event.published
        assert event.community == member.community
        assert event.owner == member.member
        assert event.title == "test"

    def test_create_and_save_private(self, client, member):
        data = {
            "title": "test",
            "description": "test",
            "starts": timezone.now(),
            "timezone": "UTC",
            "allow_comments": "true",
            "url": "",
        }
        response = client.post("/api/events/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        event = Event.objects.first()
        assert event.published is None
        assert event.community == member.community
        assert event.owner == member.member
        assert event.title == "test"

    def test_publish(self, client, member):
        event = EventFactory(
            owner=member.member, community=member.community, published=None
        )
        response = client.post(f"/api/events/{event.id}/publish/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        event.refresh_from_db()
        assert event.published

    def test_publish_if_not_owner(self, client, event, member):
        response = client.post(f"/api/events/{event.id}/publish/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_bookmark(self, client, event, member):
        response = client.post(f"/api/events/{event.id}/add_bookmark/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert (
            Bookmark.objects.filter(user=member.member).first().content_object == event
        )

    def test_like_if_owner(self, client, member):
        event = EventFactory(owner=member.member, community=member.community,)
        response = client.post(f"/api/events/{event.id}/like/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_like_if_not_owner(self, client, event, member):
        response = client.post(f"/api/events/{event.id}/like/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Like.objects.filter(user=member.member).count() == 1
        assert (
            Notification.objects.filter(recipient=event.owner, verb="like").count() == 1
        )

    def test_dislike(self, client, event, member):
        Like.objects.create(
            user=member.member,
            content_object=event,
            community=member.community,
            recipient=event.owner,
        )
        response = client.delete(f"/api/events/{event.id}/dislike/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Like.objects.filter(user=member.member).count() == 0

    def test_add_comment(self, client, event, member):
        data = {"content": "test comment"}
        response = client.post(
            f"/api/events/{event.id}/add_comment/", data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        comment = Comment.objects.first()
        assert comment.owner == member.member
        assert comment.content_object == event
        assert (
            Notification.objects.filter(
                recipient=event.owner, verb="new_comment"
            ).count()
            == 1
        )

    def test_add_comment_if_not_allowed(self, client, member):
        event = EventFactory(
            community=member.community, owner=member.member, allow_comments=False
        )
        data = {"content": "test comment"}
        response = client.post(
            f"/api/events/{event.id}/add_comment/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pin(self, client, event, moderator):
        response = client.post(f"/api/events/{event.id}/pin/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        event.refresh_from_db()
        assert event.is_pinned
        assert event.is_pinned

    def test_comments(self, client, event, member):
        CommentFactory.create_batch(
            3, owner=member.member, community=member.community, content_object=event
        )
        response = client.get(f"/api/events/{event.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
