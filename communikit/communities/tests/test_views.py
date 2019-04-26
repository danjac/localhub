import pytest

from django.http import Http404, HttpResponse
from django.test.client import RequestFactory
from django.views.generic import View

from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin

pytestmark = pytest.mark.django_db


class MyView(CommunityRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


my_view = MyView.as_view()


class TestCommunityRequiredMixin:
    def test_community_available(
        self, community: Community, req_factory: RequestFactory
    ):
        req = req_factory.get("/")
        req.community = community
        assert my_view(req).status_code == 200

    def test_community_not_available(self, req_factory: RequestFactory):
        req = req_factory.get("/")
        req.community = None
        with pytest.raises(Http404):
            my_view(req)
