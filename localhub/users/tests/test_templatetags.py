# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser
from django.template import engines

from ..factories import UserFactory
from ..templatetags.users_tags import avatar

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


class TestDismissable:
    template = """
    {% load users_tags %}
    {% dismissable user "private-stash" "toast-primary" %}
    This is your Private Stash
    {% enddismissable %}
    """

    def render_template(self, context):
        return engines["django"].from_string(self.template).render(context)

    def test_if_anonymous(self):
        content = self.render_template({"user": AnonymousUser()})
        assert "This is your Private Stash" in content

    def test_if_not_dismissed(self, user):
        content = self.render_template({"user": user})
        assert "This is your Private Stash" in content

    def test_if__dismissed(self, user):
        user.dismissed_notices.append("private-stash")
        content = self.render_template({"user": user})
        assert "This is your Private Stash" not in content
