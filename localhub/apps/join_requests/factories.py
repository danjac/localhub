# Third Party Libraries
from factory import DjangoModelFactory, SubFactory

# Localhub
# Social-BFG
from localhub.apps.communities.factories import CommunityFactory
from localhub.apps.users.factories import UserFactory

# Local
from .models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
