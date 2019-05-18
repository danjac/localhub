from factory import DjangoModelFactory, SubFactory, Faker

from communikit.communities.tests.factories import CommunityFactory
from communikit.posts.models import Post
from communikit.users.tests.factories import UserFactory


class PostFactory(DjangoModelFactory):
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Post
