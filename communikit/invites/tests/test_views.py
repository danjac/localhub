import pytest

from typing import List

from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Membership
from communikit.invites.models import Invite
from communikit.invites.tests.factories import InviteFactory

pytestmark = pytest.mark.django_db


class TestInviteListView:
    def test_get(self, client: Client, admin: Membership):
        InviteFactory.create_batch(3, community=admin.community)
        response = client.get(reverse("invites:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


class TestInviteCreateView:
    def test_get(self, client: Client, admin: Membership):
        response = client.get(reverse("invites:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, admin: Membership, mailoutbox: List):
        response = client.post(
            reverse("invites:create"), {"email": "tester@gmail.com"}
        )

        assert response.url == reverse("invites:list")
        invite = Invite.objects.get()
        assert invite.community == admin.community
        assert invite.email == "tester@gmail.com"
        assert invite.sender == admin.member
        assert invite.sent

        mail = mailoutbox[0]
        assert mail.to == ["tester@gmail.com"]
