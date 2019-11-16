import factory
from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.tests.factories import CommunityFactory
from localhub.photos.models import Photo
from localhub.users.tests.factories import UserFactory


class PhotoFactory(DjangoModelFactory):
    title = Faker("text")
    image = factory.django.ImageField()
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Photo
