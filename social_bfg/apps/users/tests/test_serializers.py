# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..serializers import AuthenticatedUserSerializer, UserSerializer

pytestmark = pytest.mark.django_db


class TestUserSerializer:
    def test_serialize_user(self, user):
        data = UserSerializer(user).data
        assert data["name"] == user.name


class TestAuthenticatedUserSerializer:
    def test_serialize_auth_user(self, member):
        data = AuthenticatedUserSerializer(member.member).data
        assert data["roles"] == {member.community.id: "member"}
