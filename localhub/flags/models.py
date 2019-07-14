# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, no_type_check

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.core.utils.content_types import get_generic_related_exists
from localhub.notifications.models import Notification


class FlagAnnotationsQuerySetMixin:
    """
    Adds annotation methods to related model query set.
    """
    @no_type_check
    def with_is_flagged(self) -> models.QuerySet:
        """
        Adds True if the object has been flagged by a user.
        """
        return self.annotate(
            is_flagged=get_generic_related_exists(self.model, Flag)
        )

    @no_type_check
    def with_has_flagged(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        """
        Adds True if the user in question has flagged the object.
        """
        return self.annotate(
            has_flagged=get_generic_related_exists(
                self.model, Flag.objects.filter(user=user)
            )
        )


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
    object_id = models.PositiveIntegerField(db_index=True)
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
        indexes = [
            models.Index(
                fields=["user", "content_type", "object_id", "community"]
            )
        ]

    def notify(self) -> List[Notification]:
        """
        Sends notification to community moderators.
        """
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
