import pytest

from typing import List

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.test.client import Client, RequestFactory
from django.urls import reverse
from django.views.generic import View

from localhub.communities.models import Community, Membership, RequestCommunity
from localhub.communities.tests.factories import (
    CommunityFactory,
    MembershipFactory,
)
from localhub.communities.views import CommunityRequiredMixin

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
        req.user = AnonymousUser()
        assert my_view(req).status_code == 200

    def test_community_not_found(self, req_factory: RequestFactory):
        req = req_factory.get("/")
        req.community = RequestCommunity(req, "example.com", "example.com")
        assert my_view(req).url == reverse("community_not_found")

    def test_community_not_found_if_ajax(self, req_factory: RequestFactory):
        req = req_factory.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        req.community = RequestCommunity(req, "example.com", "example.com")
        with pytest.raises(Http404):
            my_view(req)

    def test_community_access_denied_if_anonymous(
        self, req_factory: RequestFactory
    ):
        req = req_factory.get("/")
        req.community = CommunityFactory(public=False)
        req.user = AnonymousUser()
        assert my_view(req).url.startswith(reverse("account_login"))

    def test_community_access_denied_if_private_allowed(
        self, req_factory: RequestFactory, user: settings.AUTH_USER_MODEL
    ):
        req = req_factory.get("/")
        req.community = CommunityFactory(public=False)
        req.user = user
        my_public_view = MyView.as_view(allow_if_private=True)
        assert my_public_view(req).status_code == 200

    def test_community_access_denied_if_authenticated(
        self, req_factory: RequestFactory, user: settings.AUTH_USER_MODEL
    ):
        req = req_factory.get("/")
        req.community = CommunityFactory(public=False)
        req.user = user
        assert my_view(req).url == reverse("community_access_denied")

    def test_community_access_denied_if_ajax(
        self, req_factory: RequestFactory, user: settings.AUTH_USER_MODEL
    ):
        req = req_factory.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        req.community = CommunityFactory(public=False)
        req.user = user
        with pytest.raises(PermissionDenied):
            my_view(req)


class TestCommunityDetailView:
    def test_get(self, client: Client, community: Community):
        assert (
            client.get(reverse("communities:community_detail")).status_code
            == 200
        )


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
        assert admin.community.admin == admin.member


class TestCommunityListView:
    def test_get(
        self,
        client: Client,
        member: Membership,
        user: settings.AUTH_USER_MODEL,
    ):
        MembershipFactory(member=user, community=member.community)
        assert (
            client.get(reverse("communities:community_list")).status_code
            == 200
        )


class TestMembershipListView:
    def test_get(
        self, client: Client, admin: Membership, user: settings.AUTH_USER_MODEL
    ):
        for _ in range(3):
            MembershipFactory(community=admin.community)
        response = client.get(reverse("communities:membership_list"))
        assert len(response.context["object_list"]) == 4

    def test_get_if_search(
        self, client: Client, admin: Membership, user: settings.AUTH_USER_MODEL
    ):
        for _ in range(3):
            MembershipFactory(community=admin.community)

        member = MembershipFactory(community=admin.community)

        response = client.get(
            reverse("communities:membership_list"),
            {"q": member.member.username},
        )
        assert len(response.context["object_list"]) == 1


class TestMembershipDetailView:
    def test_get(
        self, client: Client, admin: Membership, user: settings.AUTH_USER_MODEL
    ):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_detail", args=[membership.id])
            ).status_code
            == 200
        )


class TestMembershipUpdateView:
    def test_get(
        self, client: Client, admin: Membership, user: settings.AUTH_USER_MODEL
    ):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_update", args=[membership.id])
            ).status_code
            == 200
        )

    def test_post(
        self, client: Client, admin: Membership, user: settings.AUTH_USER_MODEL
    ):
        membership = MembershipFactory(member=user, community=admin.community)
        response = client.post(
            reverse("communities:membership_update", args=[membership.id]),
            {"active": True, "role": "moderator"},
        )
        assert response.url == reverse("communities:membership_list")
        membership.refresh_from_db()
        assert membership.role == "moderator"


class TestMembershipDeleteView:
    def test_get(
        self, client: Client, admin: Membership, user: settings.AUTH_USER_MODEL
    ):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_delete", args=[membership.id])
            ).status_code
            == 200
        )

    def test_delete(
        self,
        client: Client,
        admin: Membership,
        user: settings.AUTH_USER_MODEL,
        mailoutbox: List,
    ):
        membership = MembershipFactory(community=admin.community)
        response = client.post(
            reverse("communities:membership_delete", args=[membership.id])
        )

        assert response.url == reverse("communities:membership_list")
        assert not Membership.objects.filter(pk=membership.pk).exists()
        assert mailoutbox[0].to == [membership.member.email]

    def test_delete_own_membership(self, client: Client, member: Membership):
        response = client.post(
            reverse("communities:membership_delete", args=[member.id])
        )

        assert response.url == reverse("communities:community_list")
        assert not Membership.objects.filter(pk=member.id).exists()


class TestCommunityLeaveView:
    def test_get(
        self,
        client: Client,
        member: Membership,
        user: settings.AUTH_USER_MODEL,
    ):
        assert client.get(reverse("communities:leave")).status_code == 200

    def test_delete(
        self,
        client: Client,
        member: Membership,
        user: settings.AUTH_USER_MODEL,
    ):
        response = client.post(reverse("communities:leave"))

        assert response.url == "/"
        assert not Membership.objects.filter(pk=member.pk).exists()

    def test_delete_own_membership(self, client: Client, member: Membership):
        response = client.post(
            reverse("communities:membership_delete", args=[member.id])
        )

        assert response.url == reverse("communities:community_list")
        assert not Membership.objects.filter(pk=member.id).exists()
