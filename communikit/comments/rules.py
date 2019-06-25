# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from django.conf import settings

from communikit.comments.models import Comment
from communikit.activities.rules import (
    is_activity_community_member,
    is_activity_community_moderator,
)


@rules.predicate
def is_owner(user: settings.AUTH_USER_MODEL, comment: Comment) -> bool:
    return user.id == comment.owner_id


@rules.predicate
def is_comment_community_member(
    user: settings.AUTH_USER_MODEL, comment: Comment
) -> bool:
    return is_activity_community_member.test(user, comment.activity)


@rules.predicate
def is_comment_community_moderator(
    user: settings.AUTH_USER_MODEL, comment: Comment
) -> bool:
    return is_activity_community_moderator.test(user, comment.activity)


rules.add_perm("comments.create_comment", is_activity_community_member)
rules.add_perm("comments.change_comment", is_owner)
rules.add_perm(
    "comments.delete_comment", is_owner | is_comment_community_moderator
)
rules.add_perm(
    "comments.flag_comment", is_comment_community_member & ~is_owner
)
rules.add_perm(
    "comments.like_comment", is_comment_community_member & ~is_owner
)
