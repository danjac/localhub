from factory import DjangoModelFactory, SubFactory, Faker

from localite.communities.tests.factories import CommunityFactory
from localite.users.tests.factories import UserFactory
from localite.join_requests.models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
