# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import io

# Django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files import File
from django.http import HttpResponse

# Django Rest Framework
from rest_framework.test import APIRequestFactory

# Third Party Libraries
import pytest
from PIL import Image

# Social-BFG
from social_bfg.apps.comments.factories import CommentFactory
from social_bfg.apps.communities.factories import CommunityFactory, MembershipFactory
from social_bfg.apps.communities.models import Membership, RequestCommunity
from social_bfg.apps.events.factories import EventFactory
from social_bfg.apps.invites.factories import InviteFactory
from social_bfg.apps.join_requests.factories import JoinRequestFactory
from social_bfg.apps.likes.factories import LikeFactory
from social_bfg.apps.notifications.factories import NotificationFactory
from social_bfg.apps.photos.factories import PhotoFactory
from social_bfg.apps.polls.factories import PollFactory
from social_bfg.apps.posts.factories import PostFactory
from social_bfg.apps.private_messages.factories import MessageFactory
from social_bfg.apps.users.factories import UserFactory


@pytest.fixture
def api_req_factory():
    return APIRequestFactory()


@pytest.fixture
def get_response():
    return lambda req: HttpResponse()


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
def request_community(api_req_factory):
    return RequestCommunity(api_req_factory.get("/"), "example", "example.com")


@pytest.fixture
def fake_image():
    file_obj = io.BytesIO()
    image = Image.new("RGBA", size=(500, 500), color="blue")
    image.save(file_obj, "png")
    file_obj.seek(0)
    return File(file_obj, name="test.jpg")


@pytest.fixture
def send_webpush_mock(mocker):
    return mocker.patch("social_bfg.apps.notifications.tasks.send_webpush")
