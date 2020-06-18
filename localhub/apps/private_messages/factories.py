# Copyright (c) 2020 by Dan Jacob

# Third Party Libraries
from factory import DjangoModelFactory, Faker, SubFactory

# Localhub
from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.users.factories import UserFactory

# Local
from .models import Message


class MessageFactory(DjangoModelFactory):
    message = Faker("text")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)

    class Meta:
        model = Message
