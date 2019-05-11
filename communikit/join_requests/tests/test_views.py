import pytest

from typing import List

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Community, Membership
from communikit.users.tests.factories import UserFactory
from communikit.join_requests.models import JoinRequest
from communikit.join_requests.tests.factories import JoinRequestFactory

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
        assert response.url == settings.COMMUNIKIT_HOME_PAGE_URL
        join_request = JoinRequest.objects.get()
        assert join_request.sender == login_user
        assert join_request.community == community
        mail = mailoutbox[0]
        assert mail.to == [admin.email]


class TestJoinRequestAcceptView:
    def test_get_if_no_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(
            community=admin.community, sender=None
        )
        response = client.get(
            reverse("join_requests:accept", args=[join_request.id])
        )
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_accepted()
        mail = mailoutbox[0]
        assert mail.to == [join_request.email]

    def test_get_if_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.get(
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


class TestJoinRequestRejectView:
    def test_get_if_no_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(
            community=admin.community, sender=None
        )
        response = client.get(
            reverse("join_requests:reject", args=[join_request.id])
        )
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_rejected()
        mail = mailoutbox[0]
        assert mail.to == [join_request.email]

    def test_get_if_user(
        self, client: Client, mailoutbox: List, admin: Membership
    ):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.get(
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
