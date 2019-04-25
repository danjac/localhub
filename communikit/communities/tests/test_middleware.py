import pytest

from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory

from communikit.communities.models import Community
from communikit.communities.middleware import CurrentCommunityMiddleware

pytestmark = pytest.mark.django_db


def my_view(req: HttpRequest) -> HttpResponse:
    return HttpResponse()


class TestCurrentCommunityMiddleware:
    def test_if_community_available(
        self, community: Community, req_factory: RequestFactory
    ):
        mw = CurrentCommunityMiddleware(my_view)
        req = req_factory.get("/", HTTP_HOST=community.domain)
        mw(req)
        assert req.community == community

    def test_if_no_community_available(self, req_factory: RequestFactory):
        mw = CurrentCommunityMiddleware(my_view)
        req = req_factory.get("/", HTTP_HOST="example.com")
        mw(req)
        assert not req.community
