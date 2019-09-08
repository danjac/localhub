# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Rulesets for communities/memberships
"""

import rules


@rules.predicate
def is_admin(user, community):
    return community.is_admin(user)


@rules.predicate
def is_moderator(user, community):
    return community.is_moderator(user)


is_moderator = is_moderator | is_admin


@rules.predicate
def is_member(user, community):
    return community.is_member(user)


is_member = is_member | is_moderator


@rules.predicate
def is_own_membership(user, membership):
    return membership.member_id == user.id


@rules.predicate
def is_membership_community_admin(user, membership):
    return is_admin.test(user, membership.community)


rules.add_rule("communities.is_admin", is_admin)
rules.add_rule("communities.is_moderator", is_moderator)
rules.add_rule("communities.is_member", is_member)

rules.add_perm("communities.view_community", is_member)
rules.add_perm("communities.manage_community", is_admin)
rules.add_perm("communities.moderate_community", is_moderator)

rules.add_perm("communities.view_membership", is_membership_community_admin)

rules.add_perm(
    "communities.change_membership",
    is_membership_community_admin & ~is_own_membership,
)
rules.add_perm(
    "communities.delete_membership",
    is_membership_community_admin | is_own_membership,
)
