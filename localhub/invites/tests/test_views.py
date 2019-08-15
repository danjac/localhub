import pytest

from typing import List

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from localhub.communities.models import Community, Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.invites.models import Invite
from localhub.invites.tests.factories import InviteFactory
from localhub.notifications.models import Notification
from localhub.users.tests.factories import UserFactory

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


class TestInviteResendView:
    def test_get(self, client: Client, admin: Membership, mailoutbox: List):

        invite = InviteFactory(community=admin.community)
        response = client.get(reverse("invites:resend", args=[invite.id]))

        assert response.url == reverse("invites:list")
        mail = mailoutbox[0]
        assert mail.to == [invite.email]


class TestInviteDeleteView:
    def test_get(self, client: Client, admin: Membership, mailoutbox: List):

        invite = InviteFactory(community=admin.community)
        response = client.get(reverse("invites:delete", args=[invite.id]))
        assert response.status_code == 200

    def test_delete(self, client: Client, admin: Membership, mailoutbox: List):

        invite = InviteFactory(community=admin.community)
        response = client.delete(reverse("invites:delete", args=[invite.id]))
        assert response.url == reverse("invites:list")
        assert not Invite.objects.exists()


class TestInviteAcceptView:
    def test_get_user_does_not_exist(
        self, client: Client, community: Community
    ):
        invite = InviteFactory(community=community)
        response = client.get(reverse("invites:accept", args=[invite.id]))
        assert response.url.startswith(reverse("account_signup"))
        invite.refresh_from_db()
        assert invite.is_pending()

    def test_get_user_exists(self, client: Client, community: Community):
        invite = InviteFactory(community=community)
        UserFactory(email=invite.email)
        response = client.get(reverse("invites:accept", args=[invite.id]))
        assert response.url.startswith(reverse("account_login"))
        invite.refresh_from_db()
        assert invite.is_pending()

    def test_current_user_is_member(
        self, client: Client, community: Community, member: Membership
    ):
        invite = InviteFactory(
            community=member.community, email=member.member.email
        )
        response = client.get(reverse("invites:accept", args=[invite.id]))
        assert response.url == settings.HOME_PAGE_URL
        invite.refresh_from_db()
        assert invite.is_accepted()

    def test_current_user_has_wrong_email(
        self, client: Client, community: Community, member: Membership
    ):
        invite = InviteFactory(community=member.community)
        response = client.get(reverse("invites:accept", args=[invite.id]))
        assert response.url == settings.HOME_PAGE_URL
        invite.refresh_from_db()
        assert invite.is_rejected()

    def test_current_user_is_not_member(
        self,
        client: Client,
        community: Community,
        login_user: settings.AUTH_USER_MODEL,
        mailoutbox: List,
    ):
        sender = MembershipFactory(community=community).member
        sender.email_preferences = ["new_member"]
        sender.save()
        invite = InviteFactory(
            community=community, email=login_user.email, sender=sender
        )
        response = client.get(reverse("invites:accept", args=[invite.id]))
        assert response.url == settings.HOME_PAGE_URL
        assert Membership.objects.filter(
            community=community, member=login_user
        ).exists()
        invite.refresh_from_db()
        assert invite.is_accepted()
        assert Notification.objects.filter(recipient=sender).exists()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [sender.email]

    def test_invalid_invite(
        self,
        client: Client,
        community: Community,
        login_user: settings.AUTH_USER_MODEL,
    ):
        user = UserFactory()
        invite = InviteFactory(community=community, email=user.email)
        response = client.get(reverse("invites:accept", args=[invite.id]))
        assert response.url == settings.HOME_PAGE_URL
        assert not Membership.objects.filter(
            community=community, member=login_user
        ).exists()
        invite.refresh_from_db()
        assert invite.is_rejected()
