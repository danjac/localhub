import rules

from django.conf import settings

from communikit.comments.models import Comment
from communikit.content.rules import (
    is_post_community_member,
    is_post_community_moderator,
)


@rules.predicate
def is_author(user: settings.AUTH_USER_MODEL, comment: Comment) -> bool:
    return user.id == comment.author_id


@rules.predicate
def is_comment_community_member(
    user: settings.AUTH_USER_MODEL, comment: Comment
) -> bool:
    return is_post_community_member.test(user, comment.post)


@rules.predicate
def is_comment_community_moderator(
    user: settings.AUTH_USER_MODEL, comment: Comment
) -> bool:
    return is_post_community_moderator.test(user, comment.post)


rules.add_perm("comments.create_comment", is_post_community_member)
rules.add_perm("comments.change_comment", is_author)
rules.add_perm(
    "comments.delete_comment", is_author | is_comment_community_moderator
)
rules.add_perm(
    "comments.like_comment", is_comment_community_member & ~is_author
)
