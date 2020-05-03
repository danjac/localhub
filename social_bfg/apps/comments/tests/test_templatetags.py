# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils import timezone

# Third Party Libraries
import pytest

from ..templatetags.comments import render_comment

pytestmark = pytest.mark.django_db


class TestRenderComment:
    def test_render_comment(self, rf, comment, member):
        context = render_comment(rf.get("/"), member.member, comment)
        assert context["comment"] == comment
        assert context["user"] == member.member
        assert context["community"] == comment.community
        assert context["show_content"] is True

    def test_render_comment_if_deleted_owner(self, rf, comment):
        comment.deleted = timezone.now()
        context = render_comment(rf.get("/"), comment.owner, comment)
        assert context["comment"] == comment
        assert context["user"] == comment.owner
        assert context["community"] == comment.community
        assert context["show_content"] is True

    def test_render_comment_if_deleted_not_owner(self, rf, comment, member):
        comment.deleted = timezone.now()
        context = render_comment(rf.get("/"), member.member, comment)
        assert context["comment"] == comment
        assert context["user"] == member.member
        assert context["community"] == comment.community
        assert context["show_content"] is False
