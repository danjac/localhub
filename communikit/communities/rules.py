import rules

# example: for a post:
# is_post_community_member(user, post):
#  return is_member.test(user, post.community)
# is_post_community_moderator(user, post):
#  return is_moderator.test(user, post.community)
# is_post_author(user, post):
# return post.author_id == user.id
# rules.add_rule('can_add_post', is_member)
# rules.add_rule('can_edit_post', is_post_author | is_post_community_moderator)
# rules.add_rule('can_delete_post', is_post_author | is_post_community_moderator)
# rules.add_rule('can_like_post', is_post_community_member & ~is_post_author)
# rules.add_rule("can_edit_membership", ~is_own_membership & is_admin)


@rules.predicate
def is_admin(user, community):
    return community.user_has_role("admin")


@rules.predicate
def is_moderator(user, community):
    return community.user_has_role("moderator")


is_moderator = is_moderator | is_admin


@rules.predicate
def is_member(user, community):
    return community.user_has_role("member")


is_member = is_member | is_moderator

rules.add_rule("can_edit_community", is_admin)

