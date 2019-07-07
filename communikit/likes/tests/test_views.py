# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from communikit.comments.models import Comment
from communikit.events.models import Event
from communikit.likes.models import Like

pytestmark = pytest.mark.django_db


class TestLikedActivityStreamView:
    def test_get(
        self,
        client: Client,
        event: Event,
        login_user: settings.AUTH_USER_MODEL,
    ):
        Like.objects.create(
            content_object=event,
            user=login_user,
            community=event.community,
            recipient=event.owner,
        )

        response = client.get(
            reverse("likes:activities"), HTTP_HOST=event.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestLikedCommentListView:
    def test_get(
        self,
        client: Client,
        comment: Comment,
        login_user: settings.AUTH_USER_MODEL,
    ):
        Like.objects.create(
            content_object=comment,
            user=login_user,
            community=comment.community,
            recipient=comment.owner,
        )

        response = client.get(
            reverse("likes:comments"), HTTP_HOST=comment.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
