# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel

from localhub.apps.communities.models import Community
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification


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

    @dispatch
    def notify(self):
        return Notification(
            content_object=self.content_object,
            recipient=self.recipient,
            actor=self.user,
            community=self.community,
            verb="like",
        )
