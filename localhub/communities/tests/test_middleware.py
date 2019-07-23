import pytest

from django.test.client import RequestFactory

from localhub.communities.middleware import CurrentCommunityMiddleware
from localhub.communities.models import Community
from localhub.core.types import DjangoView

pytestmark = pytest.mark.django_db


class TestCurrentCommunityMiddleware:
    def test_if_community_available(
        self,
        community: Community,
        req_factory: RequestFactory,
        get_response: DjangoView,
    ):
        mw = CurrentCommunityMiddleware(get_response)
        req = req_factory.get("/", HTTP_HOST=community.domain)
        mw(req)
        assert req.community == community

    def test_if_no_community_available(
        self, req_factory: RequestFactory, get_response: DjangoView
    ):
        mw = CurrentCommunityMiddleware(get_response)
        req = req_factory.get("/", HTTP_HOST="example.com")
        mw(req)
        assert req.community.is_anonymous
