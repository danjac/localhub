# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.messageboard.forms import MessageForm

pytestmark = pytest.mark.django_db


class TestMessageForm:
    def test_clean_if_missing_both_individuals_and_groups(self):
        form = MessageForm({"subject": "testing", "message": "testing"})
        assert not form.is_valid()

    def test_get_recipients_from_individuals(self, member: Membership):
        other = MembershipFactory(community=member.community)

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "individuals": f"@{other.member.username}",
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == other.member

    def test_get_recipients_excludes_sender(self, member: Membership):

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "individuals": f"@{member.member.username}",
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.count() == 0

    def test_get_recipients_from_moderators(self, member: Membership):

        moderator = MembershipFactory(
            community=member.community, role=Membership.ROLES.moderator
        )

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "groups": ["moderators"],
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == moderator.member

    def test_get_recipients_from_admins(self, member: Membership):

        admin = MembershipFactory(
            community=member.community, role=Membership.ROLES.admin
        )

        form = MessageForm(
            {"subject": "testing", "message": "testing", "groups": ["admins"]}
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == admin.member

    def test_get_recipients_from_followers(self, member: Membership):

        follower = MembershipFactory(community=member.community)
        follower.member.following.add(member.member)

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "groups": ["followers"],
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == follower.member

    def test_get_recipients_from_multiple_sources(self, member: Membership):

        other = MembershipFactory(community=member.community)

        follower = MembershipFactory(community=member.community)
        follower.member.following.add(member.member)

        MembershipFactory(
            community=member.community, role=Membership.ROLES.moderator
        )

        blocker = MembershipFactory(community=member.community).member
        blocker.blocked.add(member.member)

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "individuals": f"@{other.member.username}",
                "groups": ["moderators", "followers"],
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.count() == 3
        assert blocker not in recipients
