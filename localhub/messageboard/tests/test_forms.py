# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.models import Membership
from localhub.messageboard.forms import MessageForm
from localhub.subscriptions.models import Subscription
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestMessageForm:
    def test_clean_if_missing_both_individuals_and_groups(self):
        form = MessageForm({"subject": "testing", "message": "testing"})
        assert not form.is_valid()

    def test_get_recipients_from_individuals(self, member: Membership):

        user = UserFactory()
        Membership.objects.create(member=user, community=member.community)

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "individuals": f"@{user.username}",
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == user

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

        user = UserFactory()
        Membership.objects.create(
            member=user,
            community=member.community,
            role=Membership.ROLES.moderator,
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
        assert recipients.get() == user

    def test_get_recipients_from_admins(self, member: Membership):

        user = UserFactory()
        Membership.objects.create(
            member=user,
            community=member.community,
            role=Membership.ROLES.admin,
        )

        form = MessageForm(
            {"subject": "testing", "message": "testing", "groups": ["admins"]}
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == user

    def test_get_recipients_from_followers(self, member: Membership):

        user = UserFactory()
        Membership.objects.create(member=user, community=member.community)

        Subscription.objects.create(
            content_object=member.member,
            community=member.community,
            subscriber=user,
        )

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "groups": ["followers"],
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.get() == user

    def test_get_recipients_from_multiple_sources(self, member: Membership):

        user = UserFactory()
        Membership.objects.create(member=user, community=member.community)

        follower = UserFactory()
        Membership.objects.create(member=follower, community=member.community)
        Subscription.objects.create(
            content_object=member.member,
            community=member.community,
            subscriber=follower,
        )

        moderator = UserFactory()
        Membership.objects.create(
            member=moderator,
            community=member.community,
            role=Membership.ROLES.moderator,
        )

        form = MessageForm(
            {
                "subject": "testing",
                "message": "testing",
                "individuals": f"@{user.username}",
                "groups": ["moderators", "followers"],
            }
        )

        assert form.is_valid()

        recipients = form.get_recipients(member.member, member.community)
        assert recipients.count() == 3
