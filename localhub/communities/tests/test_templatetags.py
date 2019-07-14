import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from localhub.communities.templatetags.communities_tags import (
    get_communities,
)

pytestmark = pytest.mark.django_db


class TestGetCommunities:
    def test_no_request(self):
        assert get_communities({}).count() == 0

    def test_anonymous_user(self, req_factory: RequestFactory):
        req = req_factory.get("/")
        req.user = AnonymousUser()
        assert get_communities({"request": req}).count() == 0

    def test_user(
        self, req_factory: RequestFactory, member: settings.AUTH_USER_MODEL
    ):
        req = req_factory.get("/")
        req.user = member.member
        assert get_communities({"request": req}).count() == 1
