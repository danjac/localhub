# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

from ..factories import PollFactory
from ..models import Poll
from ..rules import is_voting_allowed

pytestmark = pytest.mark.django_db


class TestIsVotingAllowed:
    def test_true(self, user_model):
        assert is_voting_allowed(user_model(), Poll(allow_voting=True))

    def test_false(self, user_model):
        assert not is_voting_allowed(user_model(), Poll(allow_voting=False))


class TestVotePermissions:
    def test_is_member(self, member):
        poll = PollFactory(community=member.community)
        assert member.member.has_perm("polls.vote", poll)

    def test_is_not_member(self, member):
        poll = PollFactory()
        assert not member.member.has_perm("polls.vote", poll)

    def test_is_not_published(self, member):
        poll = PollFactory(community=member.community, published=None)
        assert not member.member.has_perm("polls.vote", poll)

    def test_voting_not_allowed(self, member):
        poll = PollFactory(community=member.community, allow_voting=False)
        assert not member.member.has_perm("polls.vote", poll)
