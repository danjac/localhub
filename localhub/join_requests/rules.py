# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.communities.rules import is_admin, is_inactive_member, is_member


@rules.predicate
def is_sender(user, join_request):
    return user == join_request.sender


@rules.predicate
def is_community_admin(user, join_request):
    return is_admin(user, join_request.community)


@rules.predicate
def is_join_request_allowed(user, community):
    return community.allow_join_requests


rules.add_perm(
    "join_requests.create", is_join_request_allowed & ~is_member & ~is_inactive_member
)

rules.add_perm("join_requests.delete", is_sender | is_community_admin)
