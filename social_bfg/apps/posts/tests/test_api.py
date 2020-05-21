# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import status

# Third Party Libraries
import pytest

pytestmark = pytest.mark.django_db


class TestPostViewSet:
    def test_list_if_member(self, client, member, post):
        response = client.get("/api/posts/")
        assert len(response.data["results"]) == 1

    def test_list_if_not_member(self, client, login_user, post):
        response = client.get("/api/posts/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
