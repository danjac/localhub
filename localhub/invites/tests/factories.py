from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.invites.models import Invite
from localhub.users.tests.factories import UserFactory


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
