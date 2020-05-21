# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Third Party Libraries
import pytest

# Local
from ..permissions import IsActivityOwner, IsNotActivityOwner

pytestmark = pytest.mark.django_db


class TestIsNotActivityOwner:
    def test_is_owner(self, post, api_req_factory):
        req = api_req_factory.get("/")
        req.user = post.owner
        assert not IsNotActivityOwner().has_object_permission(req, None, post)

    def test_is_not_owner(self, post, user, api_req_factory):
        req = api_req_factory.post("/")
        req.user = user
        assert IsNotActivityOwner().has_object_permission(req, None, post)


class TestIsActivityOwner:
    def test_is_owner_if_safe(self, post, api_req_factory):
        req = api_req_factory.get("/")
        req.user = post.owner
        assert IsActivityOwner().has_object_permission(req, None, post)

    def test_is_owner_if_unsafe(self, post, api_req_factory):
        req = api_req_factory.get("/")
        req.user = post.owner
        assert IsActivityOwner().has_object_permission(req, None, post)

    def test_is_not_owner_if_safe(self, post, user, api_req_factory):
        req = api_req_factory.get("/")
        req.user = user
        assert IsActivityOwner().has_object_permission(req, None, post)

    def test_is_not_owner_if_not_safe(self, post, user, api_req_factory):
        req = api_req_factory.post("/")
        req.user = user
        assert not IsActivityOwner().has_object_permission(req, None, post)
