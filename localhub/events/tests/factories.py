from factory.fuzzy import FuzzyDateTime

from django.utils import timezone
from factory import DjangoModelFactory, SubFactory, Faker

from localhub.communities.tests.factories import CommunityFactory
from localhub.events.models import Event
from localhub.users.tests.factories import UserFactory


class EventFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)

    starts = FuzzyDateTime(timezone.now())

    class Meta:
        model = Event
