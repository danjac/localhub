# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel


from communikit.communities.models import Community


class Subscription(TimeStampedModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "content_type", "object_id"],
                name="unique_subscription",
            )
        ]
        indexes = [
            models.Index(
                fields=["content_type", "object_id", "subscriber", "community"]
            )
        ]
