# Copyright (c) 2020 by Dan Jacob

# Third Party Libraries
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

# Localhub
from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

# Local
from .models import Message


class MessageFactory(DjangoModelFactory):
    message = Faker("text")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)

    class Meta:
        model = Message
