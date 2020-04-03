# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

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
