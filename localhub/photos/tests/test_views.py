import io
import pytest

from PIL import Image

from django.conf import settings
from django.core.files import File
from django.test.client import Client
from django.urls import reverse

from pytest_mock import MockFixture

from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.likes.models import Like
from localhub.photos.tests.factories import PhotoFactory
from localhub.photos.models import Photo

pytestmark = pytest.mark.django_db


@pytest.fixture
def photo_for_member(member: Membership) -> Photo:
    return PhotoFactory(owner=member.member, community=member.community)


@pytest.fixture
def fake_image() -> File:
    file_obj = io.BytesIO()
    image = Image.new("RGBA", size=(500, 500), color="blue")
    image.save(file_obj, "png")
    file_obj.seek(0)
    return File(file_obj, name="test.jpg")


class TestPhotoCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("photos:create"))
        assert response.status_code == 200

    def test_post(
        self,
        client: Client,
        member: Membership,
        fake_image: File,
        send_notification_webpush_mock: MockFixture,
    ):
        response = client.post(
            reverse("photos:create"), {"title": "test", "image": fake_image}
        )
        photo = Photo.objects.get()
        assert response.url == photo.get_absolute_url()
        assert photo.owner == member.member
        assert photo.community == member.community


class TestPhotoUpdateView:
    def test_get(self, client: Client, photo_for_member: Photo):
        response = client.get(
            reverse("photos:update", args=[photo_for_member.id])
        )
        assert response.status_code == 200

    def test_post(
        self,
        client: Client,
        photo_for_member: Photo,
        fake_image: File,
        send_notification_webpush_mock: MockFixture,
    ):
        response = client.post(
            reverse("photos:update", args=[photo_for_member.id]),
            {"title": "UPDATED", "image": fake_image},
        )
        photo_for_member.refresh_from_db()
        assert response.url == photo_for_member.get_absolute_url()
        assert photo_for_member.title == "UPDATED"


class TestPhotoDeleteView:
    def test_get(self, client: Client, photo_for_member: Photo):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("photos:delete", args=[photo_for_member.id])
        )
        assert response.status_code == 200

    def test_delete(self, client: Client, photo_for_member: Photo):
        response = client.delete(
            reverse("photos:delete", args=[photo_for_member.id])
        )
        assert response.url == reverse("activities:stream")
        assert Photo.objects.count() == 0


class TestPhotoDetailView:
    def test_get(self, client: Client, photo: Photo):
        response = client.get(
            photo.get_absolute_url(), HTTP_HOST=photo.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" not in response.context

    def test_get_if_can_photo_comment(
        self,
        client: Client,
        photo: Photo,
        login_user: settings.AUTH_USER_MODEL,
    ):
        Membership.objects.create(member=login_user, community=photo.community)
        response = client.get(
            photo.get_absolute_url(), HTTP_HOST=photo.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" in response.context


class TestPhotoLikeView:
    def test_post(
        self,
        client: Client,
        member: Membership,
        send_notification_webpush_mock: MockFixture,
    ):
        photo = PhotoFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("photos:like", args=[photo.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = Like.objects.get()
        assert like.user == member.member
        assert like.recipient == photo.owner


class TestPhotoDislikeView:
    def test_post(self, client: Client, member: Membership):
        photo = PhotoFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        Like.objects.create(
            user=member.member,
            content_object=photo,
            community=photo.community,
            recipient=photo.owner,
        )
        response = client.post(
            reverse("photos:dislike", args=[photo.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert Like.objects.count() == 0
