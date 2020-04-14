# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from django.utils import timezone

from localhub.activities.rules import (
    is_activity_community_member,
    is_published,
    is_deleted,
)


@rules.predicate
def has_started(user, event):
    return event.starts < timezone.now()


rules.add_perm(
    "events.attend",
    is_activity_community_member & is_published & ~is_deleted & ~has_started,
)
