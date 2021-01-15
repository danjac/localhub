# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.core.exceptions import PermissionDenied

# Third Party Libraries
import pytest

# Local
from ..utils import extract_mentions, has_perm_or_403, linkify_mentions, user_display

pytestmark = pytest.mark.django_db


class TestHasPermOr403:
    def test_has_permission(self, user):
        has_perm_or_403(user, "users.change_user", obj=user)

    def test_does_not_have_permission(self, user):
        with pytest.raises(PermissionDenied):
            has_perm_or_403(user, "users.follow_user", obj=user)

    def test_anonymous_has_permission(self, anonymous_user, user):
        with pytest.raises(PermissionDenied):
            has_perm_or_403(anonymous_user, "users.follow_user", obj=user)


class TestUserDisplay:
    def test_user_display_with_name(self, user_model):
        user = user_model(name="Test Person")
        assert user_display(user) == "Test Person"

    def test_user_display_no_name(self, user_model):
        user = user_model(username="tester")
        assert user_display(user) == "tester"


class TestLinkifyMentions:
    def test_linkify(self):
        content = "hello @danjac"
        replaced = linkify_mentions(content)
        assert 'href="/people/danjac/"' in replaced

    def test_linkify_unicode(self):
        content = "hello @kesämies"
        replaced = linkify_mentions(content)
        assert 'href="/people/kesamies/"' in replaced


class TestExtractMentions:
    def test_extract(self):
        content = "hello @danjac and @weegill and @kesämies and @someone-else!"
        assert extract_mentions(content) == {
            "danjac",
            "weegill",
            "kesämies",
            "someone-else",
        }
