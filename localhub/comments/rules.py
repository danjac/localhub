# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.communities.rules import is_member, is_moderator


@rules.predicate
def is_owner(user, comment):
    return user.id == comment.owner_id


@rules.predicate
def is_comment_community_member(user, comment):
    return is_member.test(user, comment.community)


@rules.predicate
def is_comment_community_moderator(user, comment):
    return is_moderator.test(user, comment.community)


rules.add_perm("comments.change_comment", is_owner)
rules.add_perm("comments.delete_comment", is_owner | is_comment_community_moderator)
rules.add_perm("comments.flag_comment", is_comment_community_member & ~is_owner)
rules.add_perm("comments.like_comment", is_comment_community_member & ~is_owner)
rules.add_perm("comments.reply_to_comment", is_comment_community_member & ~is_owner)
