# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.users.factories import UserFactory

from ..factories import JoinRequestFactory
from ..models import JoinRequest

pytestmark = pytest.mark.django_db


class TestJoinRequestManager:
    def test_search(self, transactional_db):
        user = UserFactory(name="Tester")
        req = JoinRequestFactory(sender=user)
        assert JoinRequest.objects.search("tester").first() == req
