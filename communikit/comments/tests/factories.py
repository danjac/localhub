from factory import DjangoModelFactory, Faker, SubFactory

from communikit.comments.models import Comment
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    content = Faker("text")
    owner = SubFactory(UserFactory)
    activity = SubFactory(PostFactory)

    class Meta:
        model = Comment
