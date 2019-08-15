import pytest

from typing import List

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from localhub.communities.models import Community, Membership
from localhub.users.tests.factories import UserFactory
from localhub.join_requests.models import JoinRequest
from localhub.join_requests.tests.factories import JoinRequestFactory

pytestmark = pytest.mark.django_db


class TestJoinRequestListView:
    def test_get(self, client: Client, admin: Membership):
        JoinRequestFactory.create_batch(3, community=admin.community)
        response = client.get(reverse("join_requests:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


class TestJoinRequestCreateView:
    def test_get(
        self,
        client: Client,
        login_user: settings.AUTH_USER_MODEL,
        community: Community,
    ):
        assert client.get(reverse("join_requests:create")).status_code == 200

    def test_post(
        self,
        client: Client,
        mailoutbox: List,
        login_user: settings.AUTH_USER_MODEL,
        community: Community,
    ):

        admin = UserFactory()
        Membership.objects.create(
            community=community, member=admin, role=Membership.ROLES.admin
        )
        response = client.post(reverse("join_requests:create"))
        assert response.url == settings.HOME_PAGE_URL
        join_request = JoinRequest.objects.get()
        assert join_request.sender == login_user
        assert join_request.community == community
        mail = mailoutbox[0]
        assert mail.to == [admin.email]


class TestJoinRequestAcceptView:
    def test_post_if_no_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(
            community=admin.community, sender=None
        )
        response = client.post(
            reverse("join_requests:accept", args=[join_request.id])
        )
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_accepted()
        mail = mailoutbox[0]
        assert mail.to == [join_request.email]

    def test_post_if_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        admin.member.email_preferences = ["new_member"]
        admin.member.save()
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(
            reverse("join_requests:accept", args=[join_request.id])
        )
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_accepted()
        assert Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        mail = mailoutbox[0]
        assert mail.to == [join_request.sender.email]
        other_member_mail = mailoutbox[1]
        assert other_member_mail.to == [admin.member.email]


class TestJoinRequestRejectView:
    def test_post_if_no_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(
            community=admin.community, sender=None
        )
        response = client.post(
            reverse("join_requests:reject", args=[join_request.id])
        )
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_rejected()
        mail = mailoutbox[0]
        assert mail.to == [join_request.email]

    def test_post_if_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(
            reverse("join_requests:reject", args=[join_request.id])
        )
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_rejected()
        assert not Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        mail = mailoutbox[0]
        assert mail.to == [join_request.sender.email]
