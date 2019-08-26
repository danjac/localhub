import pytest


from localhub.private_messages.models import Message
from localhub.private_messages.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestMessageManager:
    def test_with_sender_has_blocked_if_not_blocked(self):
        message = MessageFactory()

        assert (
            not Message.objects.with_sender_has_blocked(message.recipient)
            .first()
            .sender_has_blocked
        )

    def test_with_sender_has_blocked_if_blocked(self):
        message = MessageFactory()
        message.sender.blocked.add(message.recipient)

        assert (
            Message.objects.with_sender_has_blocked(message.recipient)
            .first()
            .sender_has_blocked
        )


class TestMessageModel:
    def test_get_abbreviation(self):

        msg = Message(message="Hello\nthis is a *test*")
        assert msg.get_abbreviation() == "Hello this is a test"
