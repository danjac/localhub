# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import status

# Third Party Libraries
import pytest

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
