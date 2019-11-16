from factory import DjangoModelFactory, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.users.tests.factories import UserFactory

from ..models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
