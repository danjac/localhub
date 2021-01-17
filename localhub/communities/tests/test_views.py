# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import http

# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..factories import CommunityFactory, MembershipFactory
from ..models import Membership

pytestmark = pytest.mark.django_db


class TestCommunityDetailView:
    def test_get(self, client, member):
        assert (
            client.get(reverse("communities:community_detail")).status_code
            == http.HTTPStatus.OK
        )


class TestCommunityWelcomeView:
    def test_get_if_authenticated(self, client, community, login_user):
        assert (
            client.get(reverse("community_welcome")).status_code == http.HTTPStatus.OK
        )

    def test_get_if_member(self, client, member):
        assert client.get(reverse("community_welcome")).url == settings.HOME_PAGE_URL


class TestCommunityNotFoundView:
    def test_get_if_does_not_exist_anon_user(self, client):
        assert (
            client.get(reverse("community_not_found")).status_code == http.HTTPStatus.OK
        )

    def test_get_if_does_not_exist_auth_user(self, client, login_user):
        assert (
            client.get(reverse("community_not_found")).status_code == http.HTTPStatus.OK
        )

    def test_community_does_exist(self, client, member):
        assert client.get(reverse("community_not_found")).url == settings.HOME_PAGE_URL


class TestCommunityTermsView:
    def test_get(self, client, member):
        assert (
            client.get(reverse("communities:community_terms")).status_code
            == http.HTTPStatus.OK
        )


class TestCommunityUpdateView:
    def test_get(self, client, admin):
        assert (
            client.get(reverse("communities:community_update")).status_code
            == http.HTTPStatus.OK
        )

    def test_post(self, client, admin):
        url = reverse("communities:community_update")
        response = client.post(
            url, {"name": "New name", "description": "", "public": True}
        )
        assert response.url == url
        admin.community.refresh_from_db()
        assert admin.community.name == "New name"


class TestCommunityListView:
    def test_get_if_member(self, client, member):
        CommunityFactory.create_batch(3)
        response = client.get(reverse("community_list"))
        assert len(response.context["object_list"]) == 4

    def test_get_if_anonymous(self, client, community):
        CommunityFactory.create_batch(3)
        response = client.get(reverse("community_list"))
        assert len(response.context["object_list"]) == 4

    def test_get_if_not_member(self, client, login_user, community):
        CommunityFactory.create_batch(3)
        response = client.get(reverse("community_list"), HTTP_HOST=community.domain)
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
            reverse("communities:membership_list"),
            {"q": member.member.username},
        )
        assert len(response.context["object_list"]) == 1


class TestMembershipDetailView:
    def test_get(self, client, admin, user):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_detail", args=[membership.id])
            ).status_code
            == http.HTTPStatus.OK
        )


class TestMembershipUpdateView:
    def test_get(self, client, admin, user):
        membership = MembershipFactory(member=user, community=admin.community)
        assert (
            client.get(
                reverse("communities:membership_update", args=[membership.id])
            ).status_code
            == http.HTTPStatus.OK
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
        assert (
            client.get(reverse("communities:membership_leave")).status_code
            == http.HTTPStatus.OK
        )

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
