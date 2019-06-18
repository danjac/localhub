# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from model_utils import FieldTracker
from model_utils.models import TimeStampedModel

from communikit.activities.models import Activity
from communikit.core.markdown.fields import MarkdownField
from communikit.notifications.models import Notification


class CommentQuerySet(models.QuerySet):
    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(num_likes=models.Count("like"))

    def with_has_liked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        if user.is_authenticated:
            return self.annotate(
                has_liked=models.Exists(
                    Like.objects.filter(
                        user=user, comment=models.OuterRef("pk")
                    )
                )
            )
        return self.annotate(
            has_liked=models.Value(False, output_field=models.BooleanField())
        )


class Comment(TimeStampedModel):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    content = MarkdownField()
    content_tracker = FieldTracker(["content"])

    notifications = GenericRelation(Notification, related_query_name="comment")

    objects = CommentQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.activity.community.resolve_url(self.get_absolute_url())

    def notify(self, created: bool) -> List[Notification]:
        notifications: List[Notification] = []
        # notify anyone @mentioned in the description
        if self.content and (created or self.content_tracker.changed()):
            notifications += [
                Notification(
                    content_object=self,
                    recipient=recipient,
                    actor=self.owner,
                    community=self.activity.community,
                    verb="mentioned",
                )
                for recipient in self.activity.community.members.matches_usernames(  # noqa
                    self.content.extract_mentions()
                ).exclude(
                    pk=self.owner_id
                )
            ]
        # notify all community moderators
        verb = "created" if created else "updated"
        notifications += [
            Notification(
                content_object=self,
                recipient=recipient,
                actor=self.owner,
                community=self.activity.community,
                verb=verb,
            )
            for recipient in self.activity.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        # notify the activity owner
        if created and self.owner_id != self.activity.owner_id:
            notifications.append(
                Notification(
                    content_object=self,
                    actor=self.owner,
                    recipient=self.activity.owner,
                    community=self.activity.community,
                    verb="commented",
                )
            )
        Notification.objects.bulk_create(notifications)
        return notifications


class Like(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "comment")
