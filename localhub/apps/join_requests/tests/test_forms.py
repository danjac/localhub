# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
# Social-BFG
from localhub.apps.communities.factories import CommunityFactory

# Local
from ..forms import JoinRequestForm
from ..models import JoinRequest

pytestmark = pytest.mark.django_db


class JoinRequestFormTests:
    def test_if_valid(self, client, login_user):
        community = CommunityFactory()
        form = JoinRequestForm(login_user, community, data={"intro": ""})
        assert not form.is_valid()

    def test_if_blacklist(self, client, login_user):
        community = CommunityFactory(blacklisted_email_addresses=login_user.email)
        form = JoinRequestForm(login_user, community, data={"intro": ""})
        assert not form.is_valid()

    def test_if_already_request(self, client, community, login_user):
        JoinRequest.objects.create(community=community, sender=login_user)
        form = JoinRequestForm(login_user, community, data={"intro": ""})
        assert not form.is_valid()
