import operator

from functools import reduce
from typing import Callable

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models

from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel


from communikit.communities.models import Community
from communikit.likes.models import Like


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    likes = GenericRelation(Like, related_query_name="%(app_label)s_%(class)s")

    search_document = SearchVectorField(null=True)

    objects = InheritanceManager()

    class Meta:
        indexes = [GinIndex(fields=["search_document"])]

    # https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/
    def search_index_components(self):
        return {}

    # in post_save: transaction.on_commit(instance.make_search_updater())
    # set up signal for each subclass
    def make_search_updater(self) -> Callable:
        def on_commit():
            search_vectors = [
                SearchVector(models.Value(text), weight=weight)
                for (weight, text) in self.search_index_components().items()
            ]
            self.__class__.objects.filter(pk=self.pk).update(
                search_document=reduce(operator.add, search_vectors)
            )

        return on_commit
