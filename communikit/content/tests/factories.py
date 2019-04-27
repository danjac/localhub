from factory import DjangoModelFactory, SubFactory, Faker

from communikit.communities.tests.factories import CommunityFactory
from communikit.users.tests.factories import UserFactory
from communikit.content.models import Post


class PostFactory(DjangoModelFactory):
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    author = SubFactory(UserFactory)

    class Meta:
        model = Post
