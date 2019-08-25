# Copyright (c) 2019 by Dan Jacob

from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.private_messages.models import Message
from localhub.users.tests.factories import UserFactory


class MessageFactory(DjangoModelFactory):
    message = Faker("text")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)

    class Meta:
        model = Message
