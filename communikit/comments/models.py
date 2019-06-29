# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List

from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from model_utils import FieldTracker
from model_utils.models import TimeStampedModel

from communikit.communities.models import Community
from communikit.core.markdown.fields import MarkdownField
from communikit.flags.models import Flag, FlagAnnotationsQuerySetMixin
from communikit.likes.models import Like, LikeAnnotationsQuerySetMixin
from communikit.notifications.models import Notification


class CommentAnnotationsQuerySetMixin:
    def with_num_comments(self) -> models.QuerySet:
        return self.annotate(
            num_comments=models.Subquery(
                Comment.objects.filter(
                    object_id=models.OuterRef("pk"),
                    content_type=ContentType.objects.get_for_model(self.model),
                )
                # GROUP BY object id, filtering by object_id and content type
                # so subquery just has one row
                .values("object_id")
                # how many rows per group
                .annotate(count=models.Count("pk"))
                .values("count"),
                output_field=models.IntegerField(),
            )
        )


class CommentQuerySet(
    FlagAnnotationsQuerySetMixin, LikeAnnotationsQuerySetMixin, models.QuerySet
):
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


class Comment(TimeStampedModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    content = MarkdownField()
    content_tracker = FieldTracker(["content"])

    flags = GenericRelation(Flag, related_query_name="comment")
    likes = GenericRelation(Like, related_query_name="comment")
    notifications = GenericRelation(Notification, related_query_name="comment")

    objects = CommentQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.resolve_url(self.get_absolute_url())

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
                    community=self.community,
                    verb="mentioned",
                )
                for recipient in self.community.members.matches_usernames(  # noqa
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
                community=self.community,
                verb=verb,
            )
            for recipient in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        # notify the activity owner
        if created and self.owner_id != self.content_object.owner_id:
            notifications.append(
                Notification(
                    content_object=self,
                    actor=self.owner,
                    recipient=self.content_object.owner,
                    community=self.community,
                    verb="commented",
                )
            )
        Notification.objects.bulk_create(notifications)
        return notifications
