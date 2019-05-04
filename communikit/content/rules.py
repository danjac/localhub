import rules

from django.conf import settings

from communikit.communities.rules import is_member, is_moderator
from communikit.content.models import Post


@rules.predicate
def is_author(user: settings.AUTH_USER_MODEL, post: Post) -> bool:
    return user.id == post.author_id


@rules.predicate
def is_post_community_member(
    user: settings.AUTH_USER_MODEL, post: Post
) -> bool:
    return is_member.test(user, post.community)


@rules.predicate
def is_post_community_moderator(
    user: settings.AUTH_USER_MODEL, post: Post
) -> bool:
    return is_moderator.test(user, post.community)


is_editor = is_author | is_post_community_moderator

rules.add_perm("content.create_post", is_member)
rules.add_perm("content.change_post", is_editor)
rules.add_perm("content.delete_post", is_editor)

rules.add_perm("content.like_post", is_post_community_member & ~is_author)
