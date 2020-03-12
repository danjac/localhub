# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.http import HttpResponse

from localhub.comments.factories import CommentFactory
from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.communities.models import Membership
from localhub.events.factories import EventFactory
from localhub.photos.factories import PhotoFactory
from localhub.polls.factories import PollFactory
from localhub.posts.factories import PostFactory
from localhub.private_messages.factories import MessageFactory
from localhub.users.factories import UserFactory


@pytest.fixture
def get_response():
    def _get_response(req):
        return HttpResponse()

    return _get_response


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def community():
    return CommunityFactory(domain="testserver")


@pytest.fixture
def login_user(client):
    password = "t3SzTP4sZ"
    user = UserFactory()
    user.set_password(password)
    user.save()
    client.login(username=user.username, password=password)
    return user


@pytest.fixture
def member(client, login_user, community):
    return MembershipFactory(
        member=login_user, community=community, role=Membership.ROLES.member
    )


@pytest.fixture
def moderator(client, login_user, community):
    return MembershipFactory(
        member=login_user, community=community, role=Membership.ROLES.moderator
    )


@pytest.fixture
def admin(client, login_user, community):
    return MembershipFactory(
        member=login_user, community=community, role=Membership.ROLES.admin
    )


@pytest.fixture
def post(community):
    return PostFactory(
        community=community, owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def poll(community):
    return PollFactory(
        community=community, owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def photo(community):
    return PhotoFactory(
        community=community, owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def event(community):
    return EventFactory(
        community=community, owner=MembershipFactory(community=community).member,
    )


@pytest.fixture
def comment(post):
    return CommentFactory(
        content_object=post,
        community=post.community,
        owner=MembershipFactory(community=post.community).member,
    )


@pytest.fixture
def message(member):
    return MessageFactory(
        sender=member.member,
        recipient=MembershipFactory(community=member.community).member,
        community=member.community,
    )


@pytest.fixture
def send_notification_webpush_mock(mocker):
    return mocker.patch("localhub.notifications.models.webpush")
