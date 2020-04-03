# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.db.content_types import (
    get_generic_related_exists,
    get_generic_related_value_subquery,
)


class BookmarkAnnotationsQuerySetMixin:
    """
    Annotation methods for related model query sets.
    """

    def with_has_bookmarked(self, user, annotated_name="has_bookmarked"):
        """Checks if user has liked the objects, adding `has_liked`
        annotation.

        Args:

            user (User): user who has bookmarked the items
            annotated_name (str, optional): annotation name (default: "has_bookmarked")

        Returns:

            QuerySet
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_exists(
                    self.model, Bookmark.objects.filter(user=user)
                )
            }
        )

    def bookmarked(self, user, annotated_name="has_bookmarked"):
        """Filters queryset and returns only those which have been bookmarked.

        Args:

            user (User): user who has bookmarked the items
            annotated_name (str, optional): annotation name (default: "has_bookmarked")

        Returns:

            QuerySet
        """
        return self.with_has_bookmarked(user, annotated_name).filter(
            **{annotated_name: True}
        )

    def with_bookmarked_timestamp(self, user, annotated_name="bookmarked"):
        """Adds annotated "bookmarked" timestamp to bookmarked items.

        Args:
            user (User): user who has bookmarked the items
            annotated_name (str, optional): annotation timestamp name (default: "bookmarked")

        Returns:
            QuerySet
        """

        return self.annotate(
            **{
                annotated_name: get_generic_related_value_subquery(
                    self.model,
                    Bookmark.objects.filter(user=user),
                    "created",
                    models.DateTimeField(),
                )
            }
        )


class BookmarkQuerySet(models.QuerySet):
    def for_models(self, *models):
        """
        Returns instances of a Bookmark for a given set of models.
        """
        return self.filter(
            content_type__in=ContentType.objects.get_for_models(*models).values()
        )


class Bookmark(TimeStampedModel):

    community = models.ForeignKey(Community, related_name="+", on_delete=models.CASCADE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = BookmarkQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], name="unique_bookmark",
            )
        ]
        indexes = [models.Index(fields=["content_type", "object_id"])]
