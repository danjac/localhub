import pytest
from django.conf import settings
from django.urls import reverse

from localhub.communities.models import Membership

from ..factories import InviteFactory
from ..models import Invite

pytestmark = pytest.mark.django_db


class TestInviteListView:
    def test_get(self, client, admin):
        InviteFactory.create_batch(3, community=admin.community)
        response = client.get(reverse("invites:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


class TestInviteCreateView:
    def test_get(self, client, admin):
        response = client.get(reverse("invites:create"))
        assert response.status_code == 200

    def test_post(self, client, admin, mailoutbox):
        response = client.post(reverse("invites:create"), {"email": "tester@gmail.com"})

        assert response.url == reverse("invites:list")
        invite = Invite.objects.get()
        assert invite.community == admin.community
        assert invite.email == "tester@gmail.com"
        assert invite.sender == admin.member
        assert invite.sent

        mail = mailoutbox[0]
        assert mail.to == ["tester@gmail.com"]


class TestInviteResendView:
    def test_post(self, client, admin, mailoutbox):

        invite = InviteFactory(community=admin.community)
        response = client.post(reverse("invites:resend", args=[invite.id]))

        assert response.url == reverse("invites:list")
        mail = mailoutbox[0]
        assert mail.to == [invite.email]


class TestInviteDeleteView:
    def test_get(self, client, admin, mailoutbox):
        invite = InviteFactory(community=admin.community)
        response = client.get(reverse("invites:delete", args=[invite.id]))
        assert response.status_code == 200

    def test_post(self, client, admin, mailoutbox):
        invite = InviteFactory(community=admin.community)
        response = client.post(reverse("invites:delete", args=[invite.id]))
        assert response.url == reverse("invites:list")
        assert not Invite.objects.exists()


class TestReceivedInviteListView:
    def test_get(self, client, invite):
        response = client.get(reverse("invites:received_list"))
        assert response.status_code == 200
        assert invite in response.context["object_list"]


class TestInviteRejectView:
    def test_post(self, client, invite, login_user, mailoutbox):
        response = client.post(reverse("invites:reject", args=[invite.id]))

        assert not Membership.objects.filter(
            community=invite.community, member=login_user
        ).exists()

        assert not Invite.objects.pending().for_user(login_user).exists()

        assert response.url == settings.LOCALHUB_HOME_PAGE_URL
        assert len(mailoutbox) == 0

    def test_post_if_other_invites(self, client, invite, login_user, mailoutbox):
        InviteFactory(email=login_user.email)
        response = client.post(reverse("invites:reject", args=[invite.id]))

        assert not Membership.objects.filter(
            community=invite.community, member=login_user
        ).exists()

        assert response.url == reverse("invites:received_list")
        assert len(mailoutbox) == 0


class TestInviteDetailView:
    def test_get_current_user_is_member(self, client, community, member):
        invite = InviteFactory(community=member.community, email=member.member.email)
        response = client.get(reverse("invites:detail", args=[invite.id]))
        assert response.status_code == 404

    def test_get_current_user_has_wrong_email(self, client, community, member):
        invite = InviteFactory(community=member.community)
        response = client.get(reverse("invites:detail", args=[invite.id]))
        assert response.status_code == 404
        invite.refresh_from_db()
        assert invite.is_pending()

    def test_get_current_user_is_not_member(
        self, client, community, login_user, mailoutbox, send_webpush_mock,
    ):
        invite = InviteFactory(community=community, email=login_user.email,)
        response = client.get(reverse("invites:detail", args=[invite.id]))
        assert response.status_code == 200
        invite.refresh_from_db()
        assert invite.is_pending()


class TestInviteAcceptView:
    def test_post_current_user_is_member(self, client, community, member):
        invite = InviteFactory(community=member.community, email=member.member.email)
        response = client.post(reverse("invites:accept", args=[invite.id]))
        assert response.status_code == 404

    def test_post_current_user_has_wrong_email(self, client, login_user):
        invite = InviteFactory()
        response = client.post(reverse("invites:accept", args=[invite.id]))
        assert response.status_code == 404
        invite.refresh_from_db()
        assert invite.is_pending()

    def test_post_user_accepts(self, client, invite, login_user, mailoutbox):
        response = client.post(
            reverse("invites:accept", args=[invite.id]), {"accept": 1},
        )

        assert response.url == reverse("invites:received_list")

        assert Membership.objects.filter(
            community=invite.community, member=login_user
        ).exists()
        invite.refresh_from_db()
        assert invite.is_accepted()

        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [invite.sender.email]
