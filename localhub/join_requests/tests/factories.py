from factory import DjangoModelFactory, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.join_requests.models import JoinRequest
from localhub.users.tests.factories import UserFactory


class JoinRequestFactory(DjangoModelFactory):
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
