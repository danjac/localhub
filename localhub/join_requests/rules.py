# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.communities.rules import is_member


@rules.predicate
def is_join_request_allowed(user, community):
    return community.allow_join_requests


rules.add_perm("join_requests.create", is_join_request_allowed & ~is_member)
