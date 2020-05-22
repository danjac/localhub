# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import status

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.apps.bookmarks.models import Bookmark
from social_bfg.apps.likes.models import Like
from social_bfg.apps.notifications.models import Notification

# Local
from ..factories import PostFactory
from ..models import Post

pytestmark = pytest.mark.django_db


class TestPostViewSet:
    def test_list_if_member(self, client, member, post):
        response = client.get("/api/posts/")
        assert len(response.data["results"]) == 1

    def test_list_if_not_member(self, client, login_user, post):
        response = client.get("/api/posts/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_and_publish(self, client, member):
        data = {
            "title": "test",
            "description": "test",
            "publish": "true",
            "allow_comments": "true",
            "url": "",
        }
        response = client.post("/api/posts/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        post = Post.objects.first()
        assert post.published
        assert post.community == member.community
        assert post.owner == member.member
        assert post.title == "test"

    def test_create_and_save_private(self, client, member):
        data = {
            "title": "test",
            "description": "test",
            "allow_comments": "true",
            "url": "",
        }
        response = client.post("/api/posts/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        post = Post.objects.first()
        assert post.published is None
        assert post.community == member.community
        assert post.owner == member.member
        assert post.title == "test"

    def test_publish(self, client, member):
        post = PostFactory(
            owner=member.member, community=member.community, published=None
        )
        response = client.post(f"/api/posts/{post.id}/publish/")
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.published

    def test_publish_if_not_owner(self, client, post, member):
        response = client.post(f"/api/posts/{post.id}/publish/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_bookmark(self, client, post, member):
        response = client.post(f"/api/posts/{post.id}/add_bookmark/")
        assert response.status_code == status.HTTP_200_OK
        assert (
            Bookmark.objects.filter(user=member.member).first().content_object == post
        )

    def test_like_if_owner(self, client, member):
        post = PostFactory(owner=member.member, community=member.community,)
        response = client.post(f"/api/posts/{post.id}/like/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_like_if_not_owner(self, client, post, member):
        response = client.post(f"/api/posts/{post.id}/like/")
        assert response.status_code == status.HTTP_200_OK
        assert Like.objects.filter(user=member.member).count() == 1
        assert (
            Notification.objects.filter(recipient=post.owner, verb="like").count() == 1
        )

    def test_dislike(self, client, post, member):
        Like.objects.create(
            user=member.member,
            content_object=post,
            community=member.community,
            recipient=post.owner,
        )
        response = client.delete(f"/api/posts/{post.id}/dislike/")
        assert response.status_code == status.HTTP_200_OK
        assert Like.objects.filter(user=member.member).count() == 0
