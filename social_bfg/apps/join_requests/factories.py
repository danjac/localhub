# Third Party Libraries
from factory import DjangoModelFactory, SubFactory

# Social-BFG
from social_bfg.apps.communities.factories import CommunityFactory
from social_bfg.apps.users.factories import UserFactory

from .models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
