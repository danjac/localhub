from factory import DjangoModelFactory, SubFactory, Faker

from localhub.communities.tests.factories import CommunityFactory
from localhub.posts.models import Post
from localhub.users.tests.factories import UserFactory


class PostFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Post
