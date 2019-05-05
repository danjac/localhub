import pytest

from django.http import Http404, HttpResponse
from django.test.client import Client, RequestFactory
from django.urls import reverse
from django.views.generic import View

from communikit.communities.models import Community, Membership
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


class TestCommunityUpdateView:
    def test_get(self, client: Client, admin: Membership):
        assert (
            client.get(reverse("communities:community_update")).status_code
            == 200
        )

    def test_post(self, client: Client, admin: Membership):
        url = reverse("communities:community_update")
        response = client.post(
            url, {"name": "New name", "description": "", "public": True}
        )
        assert response.url == url
        admin.community.refresh_from_db()
        assert admin.community.name == "New name"
