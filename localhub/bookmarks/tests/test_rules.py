# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

pytestmark = pytest.mark.django_db


class TestViewBookmarksPermissions:
    def test_member_can_view_bookmarks(self, member):
        assert member.member.has_perm("bookmarks.view_bookmarks", member.community)

    def test_non_member_can_view_bookmarks(self, user, community):
        assert not user.has_perm("bookmarks.view_bookmarks", community)

    def test_anonymous_can_view_bookmarks(self, anonymous_user, community):
        assert not anonymous_user.has_perm("bookmarks.view_bookmarks", community)
