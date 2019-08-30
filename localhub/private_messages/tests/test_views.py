import pytest

from django.urls import reverse

from localhub.communities.tests.factories import MembershipFactory
from localhub.private_messages.models import Message
from localhub.private_messages.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestInboxView:
    def test_get(self, client, member):
        sender = MembershipFactory(community=member.community).member
        MessageFactory(
            community=member.community, recipient=member.member, sender=sender
        )
        response = client.get(reverse("private_messages:inbox"))
        assert len(response.context["object_list"]) == 1


class TestOutboxView:
    def test_get(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        MessageFactory(
            community=member.community,
            sender=member.member,
            recipient=recipient,
        )
        response = client.get(reverse("private_messages:outbox"))
        assert len(response.context["object_list"]) == 1


class TestMessageUpdateView:
    def test_get(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community,
            sender=member.member,
            recipient=recipient,
        )
        response = client.get(
            reverse("private_messages:message_update", args=[message.id])
        )
        assert response.status_code == 200

    def test_post(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community,
            sender=member.member,
            recipient=recipient,
        )
        response = client.post(
            reverse("private_messages:message_update", args=[message.id]),
            {"message": "updated"},
        )
        assert response.url == message.get_absolute_url()
        message.refresh_from_db()
        assert message.message == "updated"


class TestMessageDeleteView:
    def test_post(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community,
            sender=member.member,
            recipient=recipient,
        )
        response = client.post(
            reverse("private_messages:message_delete", args=[message.id])
        )
        assert response.url == reverse("private_messages:outbox")
        assert not Message.objects.exists()


class TestMessageMarkReadView:
    def test_post(self, client, member):
        sender = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community, recipient=member.member, sender=sender
        )
        response = client.post(
            reverse("private_messages:message_mark_read", args=[message.id])
        )
        assert response.url == message.get_absolute_url()
        message.refresh_from_db()
        assert message.read is not None


class TestMessageDetailView:
    def test_get_if_sender(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community,
            sender=member.member,
            recipient=recipient,
        )
        response = client.get(message.get_absolute_url())
        assert response.status_code == 200

    def test_get_if_recipient(self, client, member):
        sender = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community, recipient=member.member, sender=sender
        )
        response = client.get(message.get_absolute_url())
        assert response.status_code == 200

    def test_get_if_neither_recipient_nor_sender(self, client, member):
        sender = MembershipFactory(community=member.community).member
        recipient = MembershipFactory(community=member.community).member
        message = MessageFactory(
            community=member.community, sender=sender, recipient=recipient
        )
        response = client.get(message.get_absolute_url())
        assert response.status_code == 404


class TestMessageCreateView:
    def test_post_if_sender_blocked(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        recipient.blocked.add(member.member)
        response = client.post(
            reverse(
                "private_messages:message_create", args=[recipient.username]
            ),
            {"message": "test"},
        )
        assert response.status_code == 404

    def test_post(self, client, member, send_notification_webpush_mock):
        recipient = MembershipFactory(community=member.community).member
        response = client.post(
            reverse(
                "private_messages:message_create", args=[recipient.username]
            ),
            {"message": "test"},
        )
        message = Message.objects.get()
        assert message.get_absolute_url() == response.url
        assert message.recipient == recipient
        assert message.sender == member.member
        assert message.community == member.community

        assert send_notification_webpush_mock.called_once()

    def test_get(self, client, member):
        recipient = MembershipFactory(community=member.community).member
        response = client.get(
            reverse(
                "private_messages:message_create", args=[recipient.username]
            )
        )
        assert response.status_code == 200
