# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from localhub.activities.rules import (
    is_activity_community_member,
    is_activity_community_moderator,
    is_deleted,
    is_owner,
    is_published,
)


@rules.predicate
def has_started(user, event):
    return event.has_started()


@rules.predicate
def is_canceled(user, event):
    return event.canceled is not None


rules.add_perm(
    "events.attend",
    is_activity_community_member
    & ~is_canceled
    & is_published
    & ~is_deleted
    & ~has_started,
)

rules.add_perm(
    "events.cancel",
    (is_owner | is_activity_community_moderator)
    & ~is_canceled
    & is_published
    & ~is_deleted
    & ~has_started,
)
