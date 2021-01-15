# Standard Library
import http

# Django
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..decorators import community_required

pytestmark = pytest.mark.django_db


class TestCommunityRequired:
    def test_community_inactive_member(self, rf, member):

        member.community.active = False

        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = member.member
        req.community = member.community
        resp = my_view(req)
        assert resp.url == reverse("community_not_found")

    def test_community_inactive_non_member(self, rf, user, community):

        community.active = False

        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = user
        req.community = community
        resp = my_view(req)
        assert resp.url == reverse("community_not_found")

    def test_community_required_public_member(self, rf, member):
        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = member.member
        req.community = member.community
        resp = my_view(req)
        assert resp.status_code == http.HTTPStatus.OK

    def test_community_required_non_public_member(self, rf, member):

        member.community.public = False

        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = member.member
        req.community = member.community
        resp = my_view(req)
        assert resp.status_code == http.HTTPStatus.OK

    def test_community_required_public_non_member(self, rf, community, user):
        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = user
        req.community = community
        resp = my_view(req)
        assert resp.status_code == http.HTTPStatus.OK

    def test_community_required_non_public_non_member(self, rf, community, user):

        community.public = False

        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = user
        req.community = community
        resp = my_view(req)
        assert resp.url == reverse("community_welcome")

    def test_community_required_non_public_non_member_non_members_allowed(
        self, rf, community, user
    ):

        community.public = False

        @community_required(allow_non_members=True)
        def my_view(request):
            return HttpResponse()

        req = rf.get("/")
        req.user = user
        req.community = community
        resp = my_view(req)
        assert resp.status_code == http.HTTPStatus.OK

    def test_community_required_non_public_non_member_ajax(self, rf, community, user):

        community.public = False

        @community_required
        def my_view(request):
            return HttpResponse()

        req = rf.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        req.user = user
        req.community = community
        with pytest.raises(PermissionDenied):
            my_view(req)
