import rules

from django.conf import settings

from communikit.communities.models import Community, Membership


@rules.predicate
def is_admin(user: settings.AUTH_USER_MODEL, community: Community) -> bool:
    return community.user_has_role(user, "admin")


@rules.predicate
def is_moderator(user, community: Community) -> bool:
    return community.user_has_role(user, "moderator")


is_moderator = is_moderator | is_admin


@rules.predicate
def is_member(user: settings.AUTH_USER_MODEL, community: Community) -> bool:
    return community.user_has_role(user, "member")


is_member = is_member | is_moderator


@rules.predicate
def is_own_membership(
    user: settings.AUTH_USER_MODEL, membership: Membership
) -> bool:
    return membership.member_id == user.id


@rules.predicate
def is_membership_community_admin(
    user: settings.AUTH_USER_MODEL, membership: Membership
) -> bool:
    return is_admin.test(user, membership.community)


rules.add_rule('is_admin', is_admin)
rules.add_rule('is_moderator', is_moderator)
rules.add_rule('is_member', is_member)

rules.add_perm("communities.manage_community", is_admin)

rules.add_perm(
    "communities.change_membership",
    is_membership_community_admin & ~is_own_membership,
)
rules.add_perm(
    "communities.delete_membership",
    is_membership_community_admin & ~is_own_membership,
)
