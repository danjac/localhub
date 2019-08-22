# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.communities.rules import is_member

rules.add_perm("conversations.create_message", is_member)
