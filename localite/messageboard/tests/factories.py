# Copyright (c) 2019 by Dan Jacob

from factory import DjangoModelFactory, Faker, SubFactory

from localite.communities.tests.factories import CommunityFactory
from localite.messageboard.models import Message, MessageRecipient
from localite.users.tests.factories import UserFactory


class MessageFactory(DjangoModelFactory):
    subject = Faker("text")
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
