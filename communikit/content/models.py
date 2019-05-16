from typing import Set

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, models
from django.urls import reverse
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from model_utils.managers import InheritanceManager, InheritanceQuerySetMixin
from model_utils.models import TimeStampedModel

from communikit.communities.models import Community
from communikit.content.markdown import markdownify, extract_mentions
from communikit.likes.models import Like

"""
TBD: create ContentItem base abstract class. Comments should
be generic relations.
Create base views/mixins for e.g. likes/adding comments
"""


class PostQuerySetMixin:
    def for_community(self, community: Community) -> models.QuerySet:
        return self.filter(community=community)

    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(num_likes=models.Count("likes"))

    def with_num_comments(self) -> models.QuerySet:
        return self.annotate(num_comments=models.Count("comment"))

    def search(
        self, search_term: str, order_by: str = "-rank"
    ) -> models.QuerySet:
        search_vector = SearchVector(self.model.SEARCH_FIELDS)
        search_query = SearchQuery(self.query)
        return (
            self.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
            )
            .filter(search=search_query)
        )


class PostQuerySet(PostQuerySetMixin, models.QuerySet):
    pass


class StreamQuerySet(
    PostQuerySetMixin, InheritanceQuerySetMixin, models.QuerySet
):
    pass


class Post(TimeStampedModel):
    """
    Basic content Post with title, description and URL.
    """

    SEARCH_FIELDS = ("title", "description")

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    title = models.CharField(blank=True, max_length=255)
    description = MarkdownxField(blank=True)
    url = models.URLField(blank=True)

    likes = GenericRelation(Like, related_query_name="post")

    stream_objects = StreamQuerySet.as_manager()
    objects = PostQuerySet.as_manager()

    def __str__(self) -> str:
        return self.title or str(f"Post: {self.id}")

    def get_model_name(self) -> str:
        return self._meta.model_name

    def get_absolute_url(self) -> str:
        return reverse("content:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.domain_url(self.get_absolute_url())

    def markdown(self) -> str:
        return mark_safe(markdownify(self.description))

    def extract_mentions(self) -> Set[str]:
        """
        Return all @mentions in description
        """
        return extract_mentions(self.description)

    def like(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        If like already exists, deletes the like, otherwise
        creates new one. Returns whether user likes object or not.
        """
        try:
            self.likes.get(user=user).delete()
            return False
        except ObjectDoesNotExist:
            try:
                self.likes.create(user=user)
            except IntegrityError:
                pass
        return True
