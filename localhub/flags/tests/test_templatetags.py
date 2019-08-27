# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.flags.models import Flag
from localhub.flags.templatetags.flags_tags import get_flags_count
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestGetFlagsCount:
    def test_get_count(self, req_factory, post):
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        req = req_factory.get("/")
        req.community = post.community
        assert get_flags_count({"request": req}) == 1
