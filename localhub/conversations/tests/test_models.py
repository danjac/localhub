import pytest


from localhub.conversations.models import Message
from localhub.conversations.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestMessageManager:
    def test_with_num_replies(self):
        parent = MessageFactory()
        MessageFactory(parent=parent)
        messages = Message.objects.with_num_replies().filter(
            parent__isnull=False
        )
        assert messages.first().num_replies == 0
        messages = Message.objects.with_num_replies().filter(
            parent__isnull=True
        )
        assert messages.first().num_replies == 1


class TestMessageModel:
    def test_get_abbreviation(self):

        msg = Message(message="Hello\nthis is a *test*")
        assert msg.get_abbreviation() == "Hello this is a test"
