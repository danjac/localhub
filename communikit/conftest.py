import pytest

from django.conf import settings
from django.test import Client, RequestFactory

from communikit.users.tests.factories import UserFactory


@pytest.fixture
def req_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def login_user(client: Client) -> settings.AUTH_USER_MODEL:
    password = "t3SzTP4sZ"
    user = UserFactory()
    user.set_password(password)
    user.save()
    client.login(username=user.username, password=password)
    return user
