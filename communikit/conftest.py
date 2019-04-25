import pytest

from django.conf import settings
from django.test import Client, RequestFactory
from django.contrib.sites.models import Site

from communikit.users.tests.factories import UserFactory
from communikit.communities.models import Community
from communikit.communities.tests.factories import (
    CommunityFactory,
    SiteFactory,
)


@pytest.fixture
def req_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def site() -> Site:
    return SiteFactory()


@pytest.fixture
def community(site: Site) -> Community:
    return CommunityFactory(site=site)


@pytest.fixture
def login_user(client: Client) -> settings.AUTH_USER_MODEL:
    password = "t3SzTP4sZ"
    user = UserFactory()
    user.set_password(password)
    user.save()
    client.login(username=user.username, password=password)
    return user
