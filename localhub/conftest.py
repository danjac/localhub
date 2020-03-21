# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from localhub.comments.factories import CommentFactory
from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.communities.models import Membership
from localhub.events.factories import EventFactory
from localhub.likes.factories import LikeFactory
from localhub.notifications.factories import NotificationFactory
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
def anonymous_user():
    return AnonymousUser()


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
        member=login_user, community=community, role=Membership.Role.MEMBER
    )


@pytest.fixture
def moderator(client, login_user, community):
    return MembershipFactory(
        member=login_user, community=community, role=Membership.Role.MODERATOR
    )


@pytest.fixture
def admin(client, login_user, community):
    return MembershipFactory(
        member=login_user, community=community, role=Membership.Role.ADMIN
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
def like(post, member):
    return LikeFactory(
        content_object=post,
        community=post.community,
        user=member.member,
        recipient=post.owner,
    )


@pytest.fixture
def flag(post, member, moderator):
    return LikeFactory(
        content_object=post,
        community=post.community,
        user=member.member,
        moderator=moderator.member,
    )


@pytest.fixture
def message(member):
    return MessageFactory(
        sender=member.member,
        recipient=MembershipFactory(community=member.community).member,
        community=member.community,
    )


@pytest.fixture
def notification(post):
    return NotificationFactory(
        recipient=MembershipFactory(community=post.community).member,
        community=post.community,
        actor=post.owner,
        content_object=post,
        verb="mention",
    )


@pytest.fixture
def send_webpush_mock(mocker):
    return mocker.patch("localhub.notifications.tasks.send_webpush")
