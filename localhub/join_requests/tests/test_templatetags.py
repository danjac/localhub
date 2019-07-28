# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.models import Community
from localhub.join_requests.templatetags.join_request_tags import (
    get_pending_join_request_count,
)
from localhub.join_requests.tests.factories import JoinRequestFactory

pytestmark = pytest.mark.django_db


class TestGetPendingJoinRequestCount:
    def test_get_pending_join_request_count(self, community: Community):
        JoinRequestFactory.create_batch(3, community=community)
        assert get_pending_join_request_count(community) == 3
