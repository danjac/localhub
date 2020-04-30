# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models

from localhub.db.generic import (
    get_generic_related_count_subquery,
    get_generic_related_exists,
    get_generic_related_value_subquery,
)
from localhub.db.utils import boolean_value

from . import Like


class LikeAnnotationsQuerySetMixin:
    """
    Annotation methods for related model query sets.
    """

    def with_num_likes(self, annotated_name="num_likes"):
        """Appends the total number of likes each object has received.

        Args:
            annotated_name (str, optional): the annotation name (default: "num_likes")
        """
        return self.annotate(
            **{annotated_name: get_generic_related_count_subquery(self.model, Like)}
        )

    def exists_likes(self, user):
        return get_generic_related_exists(self.model, Like.objects.filter(user=user))

    def with_has_liked(self, user, annotated_name="has_liked"):
        """Checks if user has liked the object, adding `has_liked`
        annotation.

        Args:
            user (User): user who has liked the items
            annotated_name (str, optional): the annotation name (default: "has_liked")

        Returns:
            QuerySet
        """
        return self.annotate(
            **{
                annotated_name: boolean_value(False)
                if user.is_anonymous
                else self.exists_likes(user)
            }
        )

    def liked(self, user, annotated_name="has_liked"):
        """Filters queryset to include only liked items.

        Args:
            user (User): user who has liked the items
            annotated_name (str, optional): the annotation name (default: "has_liked")

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self.none()

        return self.filter(self.exists_likes(user)).annotate(
            **{annotated_name: boolean_value(True)}
        )

    def with_liked_timestamp(self, user, annotated_name="liked"):
        """Filters all items liked by this user and includes annotated
        "liked" timestamp.

        Args:
            user (User)
            annotated_name (str, optional): the annotation name (default: "liked")

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self.none()

        return self.annotate(
            **{
                annotated_name: get_generic_related_value_subquery(
                    self.model,
                    Like.objects.filter(user=user),
                    "created",
                    models.DateTimeField(),
                )
            }
        )
