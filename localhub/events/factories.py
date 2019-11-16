from django.utils import timezone
from factory import DjangoModelFactory, Faker, SubFactory
from factory.fuzzy import FuzzyDateTime

from localhub.communities.factories import CommunityFactory
from localhub.users.factories import UserFactory

from .models import Event


class EventFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    starts = FuzzyDateTime(timezone.now())

    class Meta:
        model = Event
