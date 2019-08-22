import pytest

from django.test.client import Client
from django.urls import reverse

from pytest_mock import MockFixture

from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.conversations.models import Message
from localhub.conversations.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestInboxView:
    def test_get(self, client: Client, member: Membership):
        MessageFactory(community=member.community, recipient=member.member)
        response = client.get(reverse("conversations:inbox"))
        assert len(response.context["object_list"]) == 1


class TestOutboxView:
    def test_get(self, client: Client, member: Membership):
        MessageFactory(community=member.community, sender=member.member)
        response = client.get(reverse("conversations:outbox"))
        assert len(response.context["object_list"]) == 1


class TestConversationView:
    def test_get(self, client: Client, member: Membership):
        other_user = MembershipFactory(community=member.community).member
        from_me = MessageFactory(
            community=member.community,
            sender=member.member,
            recipient=other_user,
        )
        to_me = MessageFactory(
            community=member.community,
            sender=other_user,
            recipient=member.member,
        )
        to_someone_else = MessageFactory(
            community=member.community, sender=other_user
        )
        response = client.get(
            reverse("conversations:conversation", args=[other_user.username])
        )
        assert response.status_code == 200

        object_list = response.context["object_list"]
        assert from_me in object_list
        assert to_me in object_list
        assert to_someone_else not in object_list


class TestMessageDeleteView:
    def test_delete(self, client: Client, member: Membership):
        message = MessageFactory(
            community=member.community, sender=member.member
        )
        response = client.delete(
            reverse("conversations:message_delete", args=[message.id])
        )
        assert response.url == reverse("conversations:outbox")
        assert not Message.objects.exists()


class TestMessageMarkReadView:
    def test_post(self, client: Client, member: Membership):
        message = MessageFactory(
            community=member.community, recipient=member.member
        )
        response = client.post(
            reverse("conversations:message_mark_read", args=[message.id])
        )
        assert response.url == message.get_absolute_url()
        message.refresh_from_db()
        assert message.read is not None


class TestMessageDetailView:
    def test_get_if_sender(self, client: Client, member: Membership):
        message = MessageFactory(
            community=member.community, sender=member.member
        )
        response = client.get(message.get_absolute_url())
        assert response.status_code == 200
        assert response.context["sender_url"] == reverse(
            "conversations:outbox"
        )
        assert response.context["recipient_url"] == reverse(
            "conversations:conversation", args=[message.recipient.username]
        )

    def test_get_if_recipient(self, client: Client, member: Membership):
        message = MessageFactory(
            community=member.community, recipient=member.member
        )
        response = client.get(message.get_absolute_url())
        assert response.status_code == 200
        assert response.context["recipient_url"] == reverse(
            "conversations:inbox"
        )
        assert response.context["sender_url"] == reverse(
            "conversations:conversation", args=[message.recipient.username]
        )

    def test_get_if_neither_recipient_nor_sender(
        self, client: Client, member: Membership
    ):
        message = MessageFactory(community=member.community)
        response = client.get(message.get_absolute_url())
        assert response.status_code == 404


class TestMessageCreateView:
    def test_post_if_sender_blocked(self, client: Client, member: Membership):
        recipient = MembershipFactory(community=member.community).member
        recipient.blocked.add(member.member)
        response = client.post(
            reverse("conversations:message_create", args=[recipient.username]),
            {"message": "test"},
        )
        assert response.status_code == 403

    def test_post(
        self,
        client: Client,
        member: Membership,
        send_notification_webpush_mock: MockFixture,
    ):
        recipient = MembershipFactory(community=member.community).member
        response = client.post(
            reverse("conversations:message_create", args=[recipient.username]),
            {"message": "test"},
        )
        assert response.url == reverse(
            "conversations:conversation", args=[recipient.username]
        )

        message = Message.objects.get()
        assert message.recipient == recipient
        assert message.sender == member.member
        assert message.community == member.community

        assert send_notification_webpush_mock.called_once()
