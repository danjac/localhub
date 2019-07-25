# Copyright (c) 2019 by Dan Jacob

from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.messageboard.models import Message, MessageRecipient
from localhub.users.tests.factories import UserFactory


class MessageFactory(DjangoModelFactory):
    subject = "Test Message"
    message = Faker("text")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Message


class MessageRecipientFactory(DjangoModelFactory):
    message = SubFactory(MessageFactory)
    recipient = SubFactory(UserFactory)

    class Meta:
        model = MessageRecipient
