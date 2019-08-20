# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory

from pytest_mock import MockFixture

from localhub.comments.models import Comment
from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Community, Membership
from localhub.communities.tests.factories import (
    CommunityFactory,
    MembershipFactory,
)
from localhub.events.models import Event
from localhub.events.tests.factories import EventFactory
from localhub.photos.models import Photo
from localhub.photos.tests.factories import PhotoFactory
from localhub.posts.models import Post
from localhub.posts.tests.factories import PostFactory
from localhub.core.types import DjangoView
from localhub.users.tests.factories import UserFactory


@pytest.fixture
def get_response() -> DjangoView:
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
    return MembershipFactory(
        member=login_user, community=community, role=Membership.ROLES.member
    )


@pytest.fixture
def moderator(
    client: Client, login_user: settings.AUTH_USER_MODEL, community: Community
) -> Membership:
    return MembershipFactory(
        member=login_user, community=community, role=Membership.ROLES.moderator
    )


@pytest.fixture
def admin(
    client: Client, login_user: settings.AUTH_USER_MODEL, community: Community
) -> Membership:
    return MembershipFactory(
        member=login_user, community=community, role=Membership.ROLES.admin
    )


@pytest.fixture
def post(community: Community) -> Post:
    return PostFactory(
        community=community,
        owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def photo(community: Community) -> Photo:
    return PhotoFactory(
        community=community,
        owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def event(community: Community) -> Event:
    return EventFactory(
        community=community,
        owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def comment(post: Post) -> Comment:
    return CommentFactory(
        content_object=post,
        community=post.community,
        owner=MembershipFactory(community=post.community).member,
    )


@pytest.fixture
def send_notification_webpush_mock(mocker: MockFixture) -> MockFixture:
    return mocker.patch("localhub.notifications.models.webpush")
