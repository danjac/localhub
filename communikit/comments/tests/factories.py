from factory import DjangoModelFactory, SubFactory, Faker

from communikit.comments.models import Comment
from communikit.content.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    content = Faker("text")
    post = SubFactory(PostFactory)
    author = SubFactory(UserFactory)

    class Meta:
        model = Comment
