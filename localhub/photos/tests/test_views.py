# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.conf import settings
from django.urls import reverse

from localhub.communities.factories import MembershipFactory
from localhub.likes.factories import LikeFactory
from localhub.likes.models import Like

from ..factories import PhotoFactory
from ..models import Photo

pytestmark = pytest.mark.django_db


class TestPhotoCreateView:
    def test_get(self, client, member):
        response = client.get(reverse("photos:create"))
        assert response.status_code == 200

    def test_post(self, client, member, fake_image, send_webpush_mock):
        response = client.post(
            reverse("photos:create"), {"title": "test", "image": fake_image}
        )
        photo = Photo.objects.get()
        assert response.url == photo.get_absolute_url()
        assert photo.owner == member.member
        assert photo.community == member.community


class TestPhotoUpdateView:
    def test_get(self, client, photo_for_member):
        response = client.get(reverse("photos:update", args=[photo_for_member.id]))
        assert response.status_code == 200

    def test_post(
        self, client, photo_for_member, fake_image, send_webpush_mock,
    ):
        response = client.post(
            reverse("photos:update", args=[photo_for_member.id]),
            {"title": "UPDATED", "image": fake_image},
        )
        photo_for_member.refresh_from_db()
        assert response.url == photo_for_member.get_absolute_url()
        assert photo_for_member.title == "UPDATED"


class TestPhotoDeleteView:
    def test_get(self, client, photo_for_member):
        # test confirmation page for non-JS clients
        response = client.get(reverse("photos:delete", args=[photo_for_member.id]))
        assert response.status_code == 200

    def test_post(self, client, photo_for_member):
        response = client.post(reverse("photos:delete", args=[photo_for_member.id]))
        assert response.url == settings.LOCALHUB_HOME_PAGE_URL
        assert Photo.objects.count() == 0


class TestPhotoDetailView:
    def test_get(self, client, photo, member):
        response = client.get(
            photo.get_absolute_url(), HTTP_HOST=photo.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" in response.context


class TestPhotoLikeView:
    def test_post(self, client, member, send_webpush_mock):
        photo = PhotoFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(reverse("photos:like", args=[photo.id]))
        assert response.url == photo.get_absolute_url()
        like = Like.objects.get()
        assert like.user == member.member
        assert like.recipient == photo.owner


class TestPhotoDislikeView:
    def test_post(self, client, member):
        photo = PhotoFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        LikeFactory(
            user=member.member,
            content_object=photo,
            community=photo.community,
            recipient=photo.owner,
        )
        response = client.post(reverse("photos:dislike", args=[photo.id]))
        assert response.url == photo.get_absolute_url()
        assert Like.objects.count() == 0
