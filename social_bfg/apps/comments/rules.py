# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules
from social_bfg.apps.communities.rules import is_member, is_moderator


@rules.predicate
def is_owner(user, comment):
    return user.id == comment.owner_id


@rules.predicate
def is_deleted(user, comment):
    return comment.deleted is not None


@rules.predicate
def is_content_object_deleted(user, comment):
    return comment.content_object is None or comment.content_object.deleted


@rules.predicate
def is_comment_community_member(user, comment):
    return is_member.test(user, comment.community)


@rules.predicate
def is_comment_community_moderator(user, comment):
    return is_moderator.test(user, comment.community)


rules.add_perm("comments.change_comment", is_owner & ~is_deleted)
rules.add_perm(
    "comments.delete_comment", is_owner | (is_comment_community_moderator & ~is_deleted)
)
rules.add_perm(
    "comments.flag_comment", is_comment_community_member & ~is_owner & ~is_deleted
)
rules.add_perm("comments.bookmark_comment", is_comment_community_member & ~is_deleted)
rules.add_perm(
    "comments.like_comment", is_comment_community_member & ~is_owner & ~is_deleted
)
rules.add_perm(
    "comments.reply_to_comment",
    is_comment_community_member & ~is_owner & ~is_deleted & ~is_content_object_deleted,
)
