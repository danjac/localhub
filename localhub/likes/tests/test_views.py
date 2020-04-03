# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse

from ..factories import LikeFactory

pytestmark = pytest.mark.django_db


class TestLikedActivityStreamView:
    def test_get(self, client, event, member):
        LikeFactory(
            content_object=event,
            user=member.member,
            community=event.community,
            recipient=event.owner,
        )

        response = client.get(
            reverse("likes:activities"), HTTP_HOST=event.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1


class TestLikedCommentListView:
    def test_get(self, client, comment, member):
        LikeFactory(
            content_object=comment,
            user=member.member,
            community=comment.community,
            recipient=comment.owner,
        )

        response = client.get(
            reverse("likes:comments"), HTTP_HOST=comment.community.domain
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
