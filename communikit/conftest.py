# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory

from communikit.comments.models import Comment
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Community, Membership
from communikit.communities.tests.factories import CommunityFactory
from communikit.events.models import Event
from communikit.events.tests.factories import EventFactory
from communikit.posts.models import Post
from communikit.posts.tests.factories import PostFactory
from communikit.core.types import HttpRequestResponse
from communikit.users.tests.factories import UserFactory


@pytest.fixture
def get_response() -> HttpRequestResponse:
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
        member=login_user, community=community, role=Membership.ROLES.member
    )


@pytest.fixture
def moderator(
    client: Client, login_user: settings.AUTH_USER_MODEL, community: Community
) -> Membership:
    return Membership.objects.create(
        member=login_user, community=community, role=Membership.ROLES.moderator
    )


@pytest.fixture
def admin(
    client: Client, login_user: settings.AUTH_USER_MODEL, community: Community
) -> Membership:
    return Membership.objects.create(
        member=login_user, community=community, role=Membership.ROLES.admin
    )


@pytest.fixture
def post() -> Post:
    return PostFactory()


@pytest.fixture
def comment() -> Comment:
    return CommentFactory()


@pytest.fixture
def event() -> Event:
    return EventFactory()
