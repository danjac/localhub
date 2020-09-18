# Third Party Libraries
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

# Localhub
from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

# Local
from .models import Invite


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
