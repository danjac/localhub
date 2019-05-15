from factory.fuzzy import FuzzyDateTime

from django.utils import timezone

from communikit.content.tests.factories import PostFactory
from communikit.events.models import Event


class EventFactory(PostFactory):
    starts = FuzzyDateTime(timezone.now())

    class Meta:
        model = Event
