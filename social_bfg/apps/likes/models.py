# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel
from social_bfg.apps.communities.models import Community
from social_bfg.apps.notifications.decorators import notify
from social_bfg.apps.notifications.models import Notification
from social_bfg.db.generic import (
    get_generic_related_count_subquery,
    get_generic_related_exists,
    get_generic_related_value_subquery,
)
from social_bfg.db.utils import boolean_value


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


class LikeQuerySet(models.QuerySet):
    def for_models(self, *models):
        """
        Returns instances of a Like for a given set of models.
        """
        return self.filter(
            content_type__in=ContentType.objects.get_for_models(*models).values()
        )


class Like(TimeStampedModel):

    community = models.ForeignKey(Community, related_name="+", on_delete=models.CASCADE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = LikeQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], name="unique_like",
            )
        ]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    @notify
    def notify(self):
        return Notification(
            content_object=self.content_object,
            recipient=self.recipient,
            actor=self.user,
            community=self.community,
            verb="like",
        )
