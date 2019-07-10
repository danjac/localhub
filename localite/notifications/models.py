# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel

from localite.communities.models import Community


class Notification(TimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    verb = models.CharField(max_length=20)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "content_type",
                    "object_id",
                    "community",
                    "actor",
                    "recipient",
                ]
            )
        ]
