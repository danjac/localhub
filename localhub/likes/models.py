# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel

from localhub.common.db.content_types import (
    get_generic_related_count_subquery,
    get_generic_related_exists,
)
from localhub.communities.models import Community
from localhub.notifications.models import Notification


class LikeAnnotationsQuerySetMixin:
    """
    Annotation methods for related model query sets.
    """

    def with_has_liked(self, user, annotated_name="has_liked"):
        """
        Checks if user has liked the object, adding `has_liked`
        annotation.
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_exists(
                    self.model, Like.objects.filter(user=user)
                )
            }
        )

    def with_num_likes(self, annotated_name="num_likes"):
        """
        Appends the total number of likes each object has received.
        """
        return self.annotate(
            **{annotated_name: get_generic_related_count_subquery(self.model, Like)}
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

    def notify(self):
        """
        Sends notification to community moderators.
        """
        notification = Notification.objects.create(
            content_object=self.content_object,
            recipient=self.recipient,
            actor=self.user,
            community=self.community,
            verb="like",
        )
        return [notification]
