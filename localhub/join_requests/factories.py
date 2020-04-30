from factory import DjangoModelFactory, SubFactory

from localhub.apps.users.factories import UserFactory
from localhub.communities.factories import CommunityFactory

from .models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
