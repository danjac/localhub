import pytest


from localhub.communities.context_processors import community
from localhub.communities.tests.factories import CommunityFactory

pytestmark = pytest.mark.django_db


class TestCommunityContextProcessor:
    def test_community(self, req_factory):
        req = req_factory.get("/")
        req.community = CommunityFactory()
        context = community(req)
        assert context["community"] == req.community
