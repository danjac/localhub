import pytest

from django.conf import settings
from django.test import Client

pytestmark = pytest.mark.django_db


class TestUserDetailView:
    def test_view(self, client: Client, login_user: settings.AUTH_USER_MODEL):
        response = client.get("/account/")
        assert response.status_code == 200
