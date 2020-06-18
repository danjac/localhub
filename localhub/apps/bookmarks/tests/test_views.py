# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import reverse

# Third Party Libraries
import pytest

# Localhub
from localhub.apps.communities.factories import MembershipFactory
from localhub.apps.private_messages.factories import MessageFactory

# Local
from ..factories import BookmarkFactory

pytestmark = pytest.mark.django_db


class TestBookmarksStreamView:
    def test_get(self, client, post, member):
        BookmarkFactory(
            content_object=post, user=member.member, community=post.community,
        )

        response = client.get(
            reverse("bookmarks:activities"), HTTP_HOST=post.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestBookmarksCommentListView:
    def test_get(self, client, comment, member):
        BookmarkFactory(
            content_object=comment, user=member.member, community=comment.community,
        )

        response = client.get(
            reverse("bookmarks:comments"), HTTP_HOST=comment.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestBookmarksMessageListView:
    def test_get(self, client, member):
        message = MessageFactory(
            community=member.community,
            recipient=member.member,
            sender=MembershipFactory(community=member.community).member,
        )
        BookmarkFactory(
            content_object=message, user=member.member, community=member.community,
        )

        response = client.get(
            reverse("bookmarks:messages"), HTTP_HOST=message.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
