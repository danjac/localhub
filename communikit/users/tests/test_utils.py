# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model

from communikit.users.utils import user_display


class TestUserDisplay:
    def test_user_display_with_name(self):
        user = get_user_model()(name="Test Person")
        assert user_display(user) == "Test Person"

    def test_user_display_no_name(self):
        user = get_user_model()(username="tester")
        assert user_display(user) == "tester"
