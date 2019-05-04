import pytest

from django.conf import settings

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_get_profile_url(self, user: settings.AUTH_USER_MODEL):
        assert user.get_profile_url() == f"/profile/{user.username}/"
