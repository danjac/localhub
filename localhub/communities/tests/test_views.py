# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.views.generic import View

from ..factories import CommunityFactory, MembershipFactory
from ..models import Membership, RequestCommunity
from ..views import CommunityRequiredMixin

pytestmark = pytest.mark.django_db


class MyView(CommunityRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


my_view = MyView.as_view()


class TestCommunityRequiredMixin:
    def test_community_available(self, member, rf):
        req = rf.get("/")
        req.community = member.community
        req.user = member.member
        assert my_view(req).status_code == 200

    def test_community_not_found(self, rf, user):
        req = rf.get("/")
        req.user = user
        req.community = RequestCommunity(req, "example.com", "example.com")
        assert my_view(req).url == reverse("community_not_found")

    def test_community_not_found_if_ajax(self, rf, user):
        req = rf.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        req.user = user
        req.community = RequestCommunity(req, "example.com", "example.com")
        with pytest.raises(Http404):
            my_view(req).url

    def test_redirect_to_community_welcome_if_anonymous(self, rf):
        req = rf.get("/")
        req.community = CommunityFactory()
        req.user = AnonymousUser()
        assert my_view(req).url == reverse("account_login") + "?next=/"

    def test_redirect_to_community_welcome_if_non_members_allowed(self, rf, user):
        req = rf.get("/")
        req.community = CommunityFactory()
        req.user = user
        my_public_view = MyView.as_view(allow_non_members=True)
        assert my_public_view(req).status_code == 200

    def test_redirect_to_community_welcome_if_authenticated(self, rf, user):
        req = rf.get("/")
        req.community = CommunityFactory()
        req.user = user
        assert my_view(req).url == reverse("community_welcome")

    def test_permission_denied_if_ajax(self, rf, user):
        req = rf.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        req.community = CommunityFactory()
        req.user = user
        with pytest.raises(PermissionDenied):
            my_view(req)


class TestCommunityDetailView:
    def test_get(self, client, member):
        assert client.get(reverse("communities:community_detail")).status_code == 200


class TestCommunityWelcomeView:
    def test_get_if_authenticated(self, client, community, login_user):
        assert client.get(reverse("community_welcome")).status_code == 200

    def test_get_if_member(self, client, member):
        assert client.get(reverse("community_welcome")).url == settings.HOME_PAGE_URL


class TestCommunityNotFoundView:
    def test_get_if_does_not_exist_anon_user(self, client):
        assert client.get(reverse("community_not_found")).status_code == 200

    def test_get_if_does_not_exist_auth_user(self, client, login_user):
        assert client.get(reverse("community_not_found")).status_code == 200

    def test_community_does_exist(self, client, member):
        assert client.get(reverse("community_not_found")).url == settings.HOME_PAGE_URL


class TestCommunityTermsView:
    def test_get(self, client, member):
        assert client.get(reverse("communities:community_terms")).status_code == 200


class TestCommunityUpdateView:
    def test_get(self, client, admin):
        assert client.get(reverse("communities:community_update")).status_code == 200

    def test_post(self, client, admin):
        url = reverse("communities:community_update")
        response = client.post(
            url, {"name": "New name", "description": "", "public": True}
        )
        assert response.url == url
        admin.community.refresh_from_db()
        assert admin.community.name == "New name"
        assert admin.community.admin == admin.member


class TestCommunityListView:
    def test_get_if_member(self, client, member):
        CommunityFactory.create_batch(3)
        response = client.get(reverse("community_list"))
        assert "communities/member_community_list.html" in [
            t.name for t in response.templates
        ]
        assert len(response.context["object_list"]) == 4

    def test_get_if_not_member(self, client, login_user, community):
        CommunityFactory.create_batch(3)
        response = client.get(reverse("community_list"), HTTP_HOST=community.domain)
        assert "communities/non_member_community_list.html" in [
            t.name for t in response.templates
        ]
        assert len(response.context["object_list"]) == 4


class TestMembershipListView:
    def test_get(self, client, admin, user):
        for _ in range(3):
            MembershipFactory(community=admin.community)
        response = client.get(reverse("communities:membership_list"))
        assert len(response.context["object_list"]) == 4

    @pytest.mark.django_db(transaction=True)
    def test_get_if_search(self, client, admin, user):
        for _ in range(3):
            MembershipFactory(community=admin.community)

        member = MembershipFactory(community=admin.community)

        response = client.get(
            reverse("communities:membership_list"), {"q": member.member.username},
        )
        assert len(response.context["object_list"]) == 1


class TestMembershipDetailView:
    def test_get(self, client, admin, user):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_detail", args=[membership.id])
            ).status_code
            == 200
        )


class TestMembershipUpdateView:
    def test_get(self, client, admin, user):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_update", args=[membership.id])
            ).status_code
            == 200
        )

    def test_post(self, client, admin, user):
        membership = MembershipFactory(member=user, community=admin.community)
        response = client.post(
            reverse("communities:membership_update", args=[membership.id]),
            {"active": True, "role": "moderator"},
        )
        assert response.url == reverse(
            "communities:membership_detail", args=[membership.id]
        )
        membership.refresh_from_db()
        assert membership.role == "moderator"


class TestMembershipDeleteView:
    def test_get(self, client, admin, user):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_delete", args=[membership.id])
            ).status_code
            == 200
        )

    def test_delete(self, client, admin, user, mailoutbox):
        membership = MembershipFactory(community=admin.community)
        response = client.post(
            reverse("communities:membership_delete", args=[membership.id])
        )

        assert response.url == reverse("communities:membership_list")
        assert not Membership.objects.filter(pk=membership.pk).exists()
        assert mailoutbox[0].to == [membership.member.email]

    def test_delete_own_membership(self, client, member):
        response = client.post(
            reverse("communities:membership_delete", args=[member.id])
        )

        assert response.url == settings.HOME_PAGE_URL
        assert not Membership.objects.filter(pk=member.id).exists()


class TestMembershipLeaveView:
    def test_get(self, client, member, user):
        assert client.get(reverse("communities:membership_leave")).status_code == 200

    def test_delete(self, client, member, user):
        response = client.post(reverse("communities:membership_leave"))

        assert response.url == "/"
        assert not Membership.objects.filter(pk=member.pk).exists()

    def test_delete_own_membership(self, client, member):
        response = client.post(
            reverse("communities:membership_delete", args=[member.id])
        )

        assert response.url == settings.HOME_PAGE_URL
        assert not Membership.objects.filter(pk=member.id).exists()
