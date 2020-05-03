from factory import DjangoModelFactory, Faker, SubFactory
from social_bfg.apps.communities.factories import CommunityFactory
from social_bfg.apps.users.factories import UserFactory

from .models import Invite


class InviteFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = Invite
