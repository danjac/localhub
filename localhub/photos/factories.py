import factory
from factory import DjangoModelFactory, Faker, SubFactory

from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

from .models import Photo


class PhotoFactory(DjangoModelFactory):
    title = Faker("text")
    image = factory.django.ImageField()
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    class Meta:
        model = Photo
