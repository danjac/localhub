# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser

from ..factories import UserFactory
from ..templatetags.users_tags import avatar, dismissable_notice

pytestmark = pytest.mark.django_db


class TestAvatar:
    def test_initial_if_name(self):
        user = UserFactory(name="Test User")
        context = avatar(user)
        assert context["initials"] == "TU"

    def test_initial_if_initials(self):
        user = UserFactory(name="testuser")
        context = avatar(user)
        assert context["initials"] == "T"


class TestDismissableNotice:
    def test_if_anonymous(self):
        context = dismissable_notice(AnonymousUser(), "private-stash", "text")
        assert context["show_notice"]

    def test_if_not_dismissed(self, user):
        context = dismissable_notice(user, "private-stash", "text")
        assert context["show_notice"]

    def test_if__dismissed(self, user):
        user.dismissed_notices.append("private-stash")
        context = dismissable_notice(user, "private-stash", "text")
        assert not context["show_notice"]
