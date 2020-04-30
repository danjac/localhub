from factory import DjangoModelFactory, Faker, SubFactory

from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.users.factories import UserFactory

from .models import Invite


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
