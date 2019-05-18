from django.contrib.contenttypes.models import ContentType

from factory import (
    DjangoModelFactory,
    Faker,
    LazyAttribute,
    SelfAttribute,
    SubFactory,
)

from communikit.comments.models import Comment
from communikit.communities.tests.factories import CommunityFactory
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    content = Faker("text")
    owner = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)
    activity = SubFactory(PostFactory)
    activity_id = SelfAttribute("activity.id")
    activity_type = LazyAttribute(
        lambda obj: ContentType.objects.get_for_model(obj.activity)
    )

    class Meta:
        model = Comment
