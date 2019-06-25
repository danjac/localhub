# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from model_utils import FieldTracker
from model_utils.models import TimeStampedModel

from communikit.activities.models import Activity
from communikit.communities.models import Community
from communikit.core.markdown.fields import MarkdownField
from communikit.flags.models import Flag
from communikit.notifications.models import Notification


class CommentQuerySet(models.QuerySet):
    def with_common_annotations(
        self, community: Community, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        """
        Combines all common annotations into a single call. Applies annotations
        conditionally e.g. if user is authenticated or not.
        """

        if user.is_authenticated:
            qs = (
                self.with_num_likes()
                .with_has_liked(user)
                .with_has_flagged(user)
            )

            if user.has_perm("community.moderate_community", community):
                qs = qs.with_is_flagged()
            return qs
        return self

    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(num_likes=models.Count("like"))

    def with_has_liked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.annotate(
            has_liked=models.Exists(
                Like.objects.filter(user=user, comment=models.OuterRef("pk"))
            )
        )

    def is_flagged(
        self, user: Optional[settings.AUTH_USER_MODEL] = None
    ) -> models.Exists:

        qs = Flag.objects.filter(
            object_id=models.OuterRef("pk"),
            content_type=ContentType.objects.get_for_model(self.model),
        )
        if user:
            qs = qs.filter(user=user)
        return models.Exists(qs)

    def with_is_flagged(self) -> models.QuerySet:
        return self.annotate(is_flagged=self.is_flagged())

    def with_has_flagged(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.annotate(has_flagged=self.is_flagged(user))


class Comment(TimeStampedModel):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    content = MarkdownField()
    content_tracker = FieldTracker(["content"])

    notifications = GenericRelation(Notification, related_query_name="comment")
    flags = GenericRelation(Flag, related_query_name="comment")

    objects = CommentQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.activity.community.resolve_url(self.get_absolute_url())

    def get_flags(self) -> models.QuerySet:
        return Flag.objects.filter(comment=self)

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
