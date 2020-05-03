# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import rules

# Social-BFG
from social_bfg.apps.activities.rules import is_activity_community_member, is_published


@rules.predicate
def is_voting_allowed(user, poll):
    return poll.allow_voting


rules.add_perm(
    "polls.vote", is_activity_community_member & is_published & is_voting_allowed
)
