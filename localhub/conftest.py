# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

import pytest

from localhub.apps.comments.factories import CommentFactory
from localhub.apps.communities.factories import CommunityFactory, MembershipFactory
from localhub.apps.communities.models import Membership
from localhub.apps.join_requests.factories import JoinRequestFactory
from localhub.apps.likes.factories import LikeFactory
from localhub.apps.notifications.factories import NotificationFactory
from localhub.apps.private_messages.factories import MessageFactory
from localhub.apps.users.factories import UserFactory
from localhub.events.factories import EventFactory
from localhub.invites.factories import InviteFactory
from localhub.photos.factories import PhotoFactory
from localhub.polls.factories import PollFactory
from localhub.posts.factories import PostFactory


@pytest.fixture
def get_response():
    def _get_response(req):
        return HttpResponse()

    return _get_response


@pytest.fixture
def user_model():
    return get_user_model()


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
def invite(login_user):
    admin = MembershipFactory(role=Membership.Role.ADMIN)
    return InviteFactory(
        community=admin.community, sender=admin.member, email=login_user.email
    )


@pytest.fixture
def join_request(login_user):
    return JoinRequestFactory(sender=login_user)


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
    return mocker.patch("localhub.apps.notifications.tasks.send_webpush")
