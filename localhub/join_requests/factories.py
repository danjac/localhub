# Third Party Libraries
from factory import DjangoModelFactory, SubFactory

# Localhub
from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

# Local
from .models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
