# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import rules

# Social-BFG
from social_bfg.apps.activities.rules import (
    is_activity_community_member,
    is_activity_community_moderator,
    is_owner,
)


@rules.predicate
def is_attendable(user, event):
    return event.is_attendable()


rules.add_perm("events.attend", is_activity_community_member & is_attendable)

rules.add_perm(
    "events.cancel", (is_owner | is_activity_community_moderator) & is_attendable
)
