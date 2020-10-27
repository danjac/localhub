# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Localhub
from localhub.communities.mixins import CommunityPermissionRequiredMixin


class BookmarksPermissionMixin(CommunityPermissionRequiredMixin):
    permission_required = "bookmarks.view_bookmarks"
