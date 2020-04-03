# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from ..models import Community, Membership

pytestmark = pytest.mark.django_db


class TestCreateCommunity:
    def test_community_with_domain_already_exists(self, community):
        with pytest.raises(CommandError):
            call_command("createcommunity", community.domain, community.name)

    def test_with_new_domain(self):
        call_command("createcommunity", "mydomain.localhub.social", "My Domain")
        community = Community.objects.first()
        assert community.name == "My Domain"
        assert community.domain == "mydomain.localhub.social"
        assert community.active

    def test_with_new_domain_and_nonexistent_user(self):
        with pytest.raises(CommandError):
            call_command(
                "createcommunity", "mydomain.localhub.social", "My Domain", admin="me",
            )
        community = Community.objects.first()
        assert community is None

    def test_with_new_domain_and_admin(self, user):
        call_command(
            "createcommunity",
            "mydomain.localhub.social",
            "My Domain",
            admin=user.username,
        )
        community = Community.objects.first()
        assert community.name == "My Domain"
        assert community.domain == "mydomain.localhub.social"
        assert community.active
        membership = Membership.objects.get(community=community, member=user)
        assert membership.role == Membership.Role.ADMIN
