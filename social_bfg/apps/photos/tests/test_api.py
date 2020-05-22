# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


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
from ..factories import PhotoFactory
from ..models import Photo

pytestmark = pytest.mark.django_db


class TestPhotoViewSet:
    def test_list_if_member(self, client, member, photo):
        response = client.get("/api/photos/")
        assert len(response.data["results"]) == 1

    def test_list_if_not_member(self, client, login_user, photo):
        response = client.get("/api/photos/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_detail(self, client, member, photo):
        response = client.get(f"/api/photos/{photo.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == photo.title

    def test_detail_if_not_community_photo(self, client, member):
        photo = PhotoFactory()
        response = client.get(f"/api/photos/{photo.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_and_publish(self, client, member, fake_image):
        data = {
            "title": "test",
            "description": "test",
            "image": fake_image,
            "publish": "true",
            "allow_comments": "true",
            "url": "",
        }
        response = client.post("/api/photos/", data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        photo = Photo.objects.first()
        assert photo.published
        assert photo.community == member.community
        assert photo.owner == member.member
        assert photo.title == "test"

    def test_create_and_save_private(self, client, member, fake_image):
        data = {
            "title": "test",
            "description": "test",
            "image": fake_image,
            "allow_comments": "true",
            "url": "",
        }
        response = client.post("/api/photos/", data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        photo = Photo.objects.first()
        assert photo.published is None
        assert photo.community == member.community
        assert photo.owner == member.member
        assert photo.title == "test"

    def test_publish(self, client, member):
        photo = PhotoFactory(
            owner=member.member, community=member.community, published=None
        )
        response = client.post(f"/api/photos/{photo.id}/publish/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        photo.refresh_from_db()
        assert photo.published

    def test_publish_if_not_owner(self, client, photo, member):
        response = client.post(f"/api/photos/{photo.id}/publish/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_bookmark(self, client, photo, member):
        response = client.post(f"/api/photos/{photo.id}/add_bookmark/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert (
            Bookmark.objects.filter(user=member.member).first().content_object == photo
        )

    def test_like_if_owner(self, client, member):
        photo = PhotoFactory(owner=member.member, community=member.community,)
        response = client.post(f"/api/photos/{photo.id}/like/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_like_if_not_owner(self, client, photo, member):
        response = client.post(f"/api/photos/{photo.id}/like/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Like.objects.filter(user=member.member).count() == 1
        assert (
            Notification.objects.filter(recipient=photo.owner, verb="like").count() == 1
        )

    def test_dislike(self, client, photo, member):
        Like.objects.create(
            user=member.member,
            content_object=photo,
            community=member.community,
            recipient=photo.owner,
        )
        response = client.delete(f"/api/photos/{photo.id}/dislike/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Like.objects.filter(user=member.member).count() == 0

    def test_add_comment(self, client, photo, member):
        data = {"content": "test comment"}
        response = client.post(
            f"/api/photos/{photo.id}/add_comment/", data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        comment = Comment.objects.first()
        assert comment.owner == member.member
        assert comment.content_object == photo
        assert (
            Notification.objects.filter(
                recipient=photo.owner, verb="new_comment"
            ).count()
            == 1
        )

    def test_add_comment_if_not_allowed(self, client, member):
        photo = PhotoFactory(
            community=member.community, owner=member.member, allow_comments=False
        )
        data = {"content": "test comment"}
        response = client.post(
            f"/api/photos/{photo.id}/add_comment/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pin(self, client, photo, moderator):
        response = client.post(f"/api/photos/{photo.id}/pin/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        photo.refresh_from_db()
        assert photo.is_pinned
        assert photo.is_pinned

    def test_comments(self, client, photo, member):
        CommentFactory.create_batch(
            3, owner=member.member, community=member.community, content_object=photo
        )
        response = client.get(f"/api/photos/{photo.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
