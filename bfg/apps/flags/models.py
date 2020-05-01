# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel

from bfg.apps.communities.models import Community
from bfg.apps.notifications.decorators import notify
from bfg.apps.notifications.models import Notification
from bfg.db.generic import get_generic_related_exists


class FlagAnnotationsQuerySetMixin:
    """
    Adds annotation methods to related model query set.
    """

    def with_is_flagged(self, annotated_name="is_flagged"):
        """
        Adds True if the object has been flagged by a user.
        """
        return self.annotate(
            **{annotated_name: get_generic_related_exists(self.model, Flag)}
        )

    def with_has_flagged(self, user, annotated_name="has_flagged"):
        """
        Adds True if the user in question has flagged the object.
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_exists(
                    self.model, Flag.objects.filter(user=user)
                )
            }
        )


class Flag(TimeStampedModel):
    class Reason(models.TextChoices):
        SPAM = "spam", _("Spam")
        ABUSE = "abuse", _("Abuse")
        RULES = "rules", _("Breach of community rules")
        ILLEGAL = "illegal_activity", _("Illegal activity")
        PR0N = "pornography", _("Pornography")
        WAREZ = "copyright", _("Breach of copyright")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

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
        max_length=30, choices=Reason.choices, default=Reason.SPAM
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], name="unique_flag",
            )
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id", "created", "-created"])
        ]

    @notify
    def notify(self):
        """
        Sends notification to community moderators.
        """
        return [
            Notification(
                content_object=self.content_object,
                recipient=moderator,
                actor=self.user,
                community=self.community,
                verb="flag",
            )
            for moderator in self.community.get_moderators()
            if moderator != self.user
        ]
