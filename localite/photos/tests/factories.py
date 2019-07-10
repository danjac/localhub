import factory

from factory import DjangoModelFactory, SubFactory, Faker

from localite.communities.tests.factories import CommunityFactory
from localite.photos.models import Photo
from localite.users.tests.factories import UserFactory


class PhotoFactory(DjangoModelFactory):
    title = Faker("text")
    image = factory.django.ImageField()
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Photo
