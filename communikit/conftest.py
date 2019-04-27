import pytest


from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory

from communikit.types import get_response_callable
from communikit.users.tests.factories import UserFactory
from communikit.communities.models import Community, Membership
from communikit.communities.tests.factories import CommunityFactory


@pytest.fixture
def get_response() -> get_response_callable:
    def _get_response(req: HttpRequest) -> HttpResponse:
        return HttpResponse()

    return _get_response


@pytest.fixture
def req_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def community() -> Community:
    return CommunityFactory(domain="testserver")


@pytest.fixture
def login_user(client: Client) -> settings.AUTH_USER_MODEL:
    password = "t3SzTP4sZ"
    user = UserFactory()
    user.set_password(password)
    user.save()
    client.login(username=user.username, password=password)
    return user


@pytest.fixture
def member(
    client: Client, login_user: settings.AUTH_USER_MODEL, community: Community
) -> Membership:
    return Membership.objects.create(
        member=login_user, community=community, role="member"
    )


@pytest.fixture
def moderator(
    client: Client, login_user: settings.AUTH_USER_MODEL, community: Community
) -> Membership:
    return Membership.objects.create(
        member=login_user, community=community, role="moderator"
    )
