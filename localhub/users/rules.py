# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Rulesets for users
"""

import rules

from django.conf import settings


@rules.predicate
def is_self(
    user: settings.AUTH_USER_MODEL, other: settings.AUTH_USER_MODEL
) -> bool:
    return user.is_authenticated and user == other


rules.add_rule("users.is_self", is_self)

rules.add_perm("users.change_user", is_self)
rules.add_perm("users.delete_user", is_self)
rules.add_perm("users.block_user", ~is_self)
rules.add_perm("users.follow_user", ~is_self)

rules.add_perm("users.follow_tag", rules.is_authenticated)
rules.add_perm("users.block_tag", rules.is_authenticated)
