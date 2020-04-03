# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.activities.rules import is_activity_community_member, is_published

rules.add_perm("polls.vote", is_activity_community_member & is_published)
