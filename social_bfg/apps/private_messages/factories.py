# Copyright (c) 2020 by Dan Jacob

from factory import DjangoModelFactory, Faker, SubFactory
from social_bfg.apps.communities.factories import CommunityFactory
from social_bfg.apps.users.factories import UserFactory

from .models import Message


class MessageFactory(DjangoModelFactory):
    message = Faker("text")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)

    class Meta:
        model = Message
