import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client

pytestmark = pytest.mark.django_db


User = get_user_model()


class TestUserDetailView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get("/users/")
        assert response.status_code == 200


class TestUserUpdateView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get("/users/~update/")
        assert response.status_code == 200

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.post("/users/~update/", {"name": "New Name"})
        assert response.url == "/users/"
        login_user.refresh_from_db()
        assert login_user.name == "New Name"


class TestUserDeleteView:
    def test_get(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get("/users/~delete/")
        assert response.status_code == 200

    def test_post(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.post("/users/~delete/")
        assert response.url == "/account/login/"
        assert User.objects.filter(username=login_user.username).count() == 0
