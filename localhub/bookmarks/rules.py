# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import rules

# Localhub
from localhub.communities.rules import is_member

rules.add_perm("bookmarks.view_bookmarks", is_member)
