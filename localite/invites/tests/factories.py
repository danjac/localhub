from factory import DjangoModelFactory, SubFactory, Faker

from localite.communities.tests.factories import CommunityFactory
from localite.users.tests.factories import UserFactory
from localite.invites.models import Invite


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
