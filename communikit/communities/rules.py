import rules


@rules.predicate
def is_admin(user, community):
    return community.user_has_role(user, "admin")


@rules.predicate
def is_moderator(user, community):
    return community.user_has_role(user, "moderator")


is_moderator = is_moderator | is_admin


@rules.predicate
def is_member(user, community):
    return community.user_has_role(user, "member")


is_member = is_member | is_moderator

rules.add_perm("communities.change_community", is_admin | rules.is_staff)
