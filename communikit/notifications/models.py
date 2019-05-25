# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel


class Notification(TimeStampedModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=20)
    is_read = models.BooleanField(default=False)

    class Meta:
        abstract = True
