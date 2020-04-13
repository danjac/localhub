# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth.models import AnonymousUser
from django.template import engines

from ..factories import UserFactory
from ..templatetags.users import avatar, strip_external_images

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
    {% load users %}
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


class TestStripExternalImages:
    def test_if_external_image_and_anon_user(self, anonymous_user):
        content = '<p><img src="https://imgur.com/funny.gif"/></p>'
        assert strip_external_images(content, anonymous_user) == content

    def test_if_external_image_and_user_show_external_images(self):
        content = '<p><img src="https://imgur.com/funny.gif"/></p>'
        user = UserFactory(show_external_images=True)
        assert strip_external_images(content, user) == content

    def test_if_external_image_and_not_user_show_external_images(self):
        content = '<p><img src="https://imgur.com/funny.gif"/></p>'
        user = UserFactory(show_external_images=False)
        assert strip_external_images(content, user) == "<p></p>"

    def test_if_internal_image_and_anon_user(self, anonymous_user, settings):
        settings.STATIC_URL = "/static/"
        content = '<p><img src="/static/funny.gif"/></p>'
        assert strip_external_images(content, anonymous_user) == content

    def test_if_internal_image_and_user_show_external_images(self, settings):
        settings.STATIC_URL = "/static/"
        content = '<p><img src="/static/funny.gif"/></p>'
        user = UserFactory(show_external_images=True)
        assert strip_external_images(content, user) == content

    def test_if_internal_image_and_not_user_show_external_images(self, settings):
        settings.STATIC_URL = "/static/"
        content = '<p><img src="/static/funny.gif"/></p>'
        user = UserFactory(show_external_images=False)
        assert strip_external_images(content, user) == content
