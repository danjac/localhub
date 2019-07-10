from factory import DjangoModelFactory, SubFactory, Faker

from localite.communities.tests.factories import CommunityFactory
from localite.posts.models import Post
from localite.users.tests.factories import UserFactory


class PostFactory(DjangoModelFactory):
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Post
