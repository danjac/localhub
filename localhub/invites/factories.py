from factory import DjangoModelFactory, Faker, SubFactory

from localhub.apps.users.factories import UserFactory
from localhub.communities.factories import CommunityFactory

from .models import Invite


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
