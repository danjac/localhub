from factory.fuzzy import FuzzyDateTime

from django.utils import timezone
from factory import DjangoModelFactory, SubFactory, Faker

from localite.communities.tests.factories import CommunityFactory
from localite.events.models import Event
from localite.users.tests.factories import UserFactory


class EventFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    starts = FuzzyDateTime(timezone.now())

    class Meta:
        model = Event
