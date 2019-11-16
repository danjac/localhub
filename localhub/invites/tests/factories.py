from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.users.tests.factories import UserFactory

from ..models import Invite


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
