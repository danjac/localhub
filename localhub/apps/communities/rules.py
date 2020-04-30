# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Rulesets for communities/memberships
"""

import rules


@rules.predicate
def is_admin(user, community):
    return user.is_admin(community)


is_admin = rules.is_authenticated & is_admin


@rules.predicate
def is_moderator(user, community):
    return user.is_moderator(community)


# admin has all moderator rights
is_moderator = rules.is_authenticated & (is_moderator | is_admin)


@rules.predicate
def is_member(user, community):
    return user.is_member(community)


# admin and moderator has all member rights

is_member = rules.is_authenticated & (is_member | is_moderator)


@rules.predicate
def is_inactive_member(user, community):
    return user.is_inactive_member(community)


is_inactive_member = rules.is_authenticated & is_inactive_member


@rules.predicate
def is_self(user, membership):
    return membership.member_id == user.id


@rules.predicate
def is_admin_member(user, membership):
    return is_admin.test(user, membership.community)


rules.add_rule("communities.is_admin", is_admin)
rules.add_rule("communities.is_moderator", is_moderator)
rules.add_rule("communities.is_member", is_member)

rules.add_perm("communities.view_community", is_member)
rules.add_perm("communities.manage_community", is_admin)
rules.add_perm("communities.moderate_community", is_moderator)

rules.add_perm("communities.view_membership", is_admin_member)

rules.add_perm(
    "communities.change_membership", is_admin_member & ~is_self,
)
rules.add_perm(
    "communities.delete_membership", is_admin_member | is_self,
)
