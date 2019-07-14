# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.communities.rules import is_member

rules.add_perm("subscriptions.create_subscription", is_member)
