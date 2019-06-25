# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from communikit.communities.models import Community
from communikit.notifications.models import Notification


class Flag(TimeStampedModel):
    REASONS = Choices(
        ("spam", _("Spam")),
        ("abuse", _("Abuse")),
        ("rules", _("Breach of community rules")),
        ("illegal_activity", _("Illegal activity")),
        ("pornography", _("Pornography")),
        ("copyright", _("Breach of copyright")),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="+"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    reason = models.CharField(
        max_length=30, choices=REASONS, default=REASONS.spam
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_flag",
            )
        ]

    def notify(self) -> List[Notification]:
        notifications = [
            Notification(
                content_object=self.content_object,
                recipient=moderator,
                actor=self.user,
                community=self.community,
                verb="flagged",
            )
            for moderator in self.community.get_moderators()
        ]

        Notification.objects.bulk_create(notifications)
        return notifications
