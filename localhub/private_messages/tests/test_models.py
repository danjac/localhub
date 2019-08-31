import pytest


from localhub.communities.tests.factories import (
    CommunityFactory,
    MembershipFactory,
)
from localhub.private_messages.models import Message
from localhub.private_messages.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestMessageManager:
    def test_for_community(self):
        community = CommunityFactory()
        message = MessageFactory(
            community=community,
            sender=MembershipFactory(community=community).member,
            recipient=MembershipFactory(community=community).member,
        )
        MessageFactory(sender=MembershipFactory(community=community).member)
        MessageFactory(
            sender=MembershipFactory(community=community, active=False).member,
            recipient=MembershipFactory(community=community).member,
        )
        MessageFactory(
            sender=MembershipFactory(
                community=CommunityFactory(), active=True
            ).member,
            recipient=MembershipFactory(community=community).member,
        )
        MessageFactory(community=community)
        MessageFactory()

        qs = Message.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == message

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
    def test_get_other_user(self):
        message = MessageFactory()
        assert message.get_other_user(message.sender) == message.recipient
        assert message.get_other_user(message.recipient) == message.sender

    def test_get_abbreviation(self):

        msg = Message(message="Hello\nthis is a *test*")
        assert msg.get_abbreviation() == "Hello this is a test"
