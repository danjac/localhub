import pytest


from localhub.communities.tests.factories import (
    CommunityFactory,
    MembershipFactory,
)
from localhub.private_messages.models import Message
from localhub.private_messages.tests.factories import MessageFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestMessageManager:
    def test_for_community(self, community):

        message = MessageFactory(
            community=community,
            sender=MembershipFactory(community=community).member,
            recipient=MembershipFactory(community=community).member,
        )

        qs = Message.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == message

    def test_for_community_if_recipient_not_member(self, community):
        MessageFactory(sender=MembershipFactory(community=community).member)
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_sender_inactive(self, community):
        MessageFactory(
            sender=MembershipFactory(community=community, active=False).member,
            recipient=MembershipFactory(community=community).member,
        )
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_sender_not_member(self, community):
        MessageFactory(
            sender=MembershipFactory(community=CommunityFactory(), active=True).member,
            recipient=MembershipFactory(community=community).member,
        )
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_neither_member(self, community):
        MessageFactory(community=community)
        assert not Message.objects.for_community(community).exists()

    def test_for_community_if_not_community_message(self, community):
        MessageFactory()
        assert not Message.objects.for_community(community).exists()

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

    def test_for_sender(self, user):
        MessageFactory(sender=user)
        assert Message.objects.for_sender(user).exists()

    def test_for_recipient(self, user):
        MessageFactory(recipient=user)
        assert Message.objects.for_recipient(user).exists()

    def test_for_recipient_if_hidden(self, user):
        MessageFactory(recipient=user, is_hidden=True)
        assert not Message.objects.for_recipient(user).exists()

    def test_for_sender_or_recipient(self, user):

        first = MessageFactory(sender=user)
        second = MessageFactory(recipient=user)
        third = MessageFactory()
        fourth = MessageFactory(recipient=user, is_hidden=True)

        messages = Message.objects.for_sender_or_recipient(user)
        assert first in messages
        assert second in messages
        assert third not in messages
        assert fourth not in messages

    def test_between(self):

        user_a = UserFactory()
        user_b = UserFactory()

        first = MessageFactory(sender=user_a, recipient=user_b)
        second = MessageFactory(recipient=user_a, sender=user_b)
        third = MessageFactory()
        fourth = MessageFactory(sender=user_a)
        fifth = MessageFactory(sender=user_b)
        sixth = MessageFactory(recipient=user_a)
        seventh = MessageFactory(recipient=user_b)
        eighth = MessageFactory(recipient=user_a, sender=user_b, is_hidden=True)

        messages = Message.objects.between(user_a, user_b)

        assert first in messages
        assert second in messages
        assert third not in messages
        assert fourth not in messages
        assert fifth not in messages
        assert sixth not in messages
        assert seventh not in messages
        assert eighth not in messages


class TestMessageModel:
    def test_get_other_user(self):
        message = MessageFactory()
        assert message.get_other_user(message.sender) == message.recipient
        assert message.get_other_user(message.recipient) == message.sender

    def test_abbreviate(self):

        msg = Message(message="Hello\nthis is a *test*")
        assert msg.abbreviate() == "Hello this is a test"
