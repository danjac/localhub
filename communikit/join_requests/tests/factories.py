from factory import DjangoModelFactory, SubFactory, Faker

from communikit.communities.tests.factories import CommunityFactory
from communikit.users.tests.factories import UserFactory
from communikit.join_requests.models import JoinRequest


class JoinRequestFactory(DjangoModelFactory):
    email = Faker("email")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)

    class Meta:
        model = JoinRequest
