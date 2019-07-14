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

from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField
from localhub.core.utils.content_types import (
    get_generic_related_count_subquery,
)
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.notifications.models import Notification


class CommentAnnotationsQuerySetMixin:
    """
    Adds comment-related annotation methods to a related model
    queryset.
    """
    def with_num_comments(self) -> models.QuerySet:
        """
        Annotates `num_comments` to the model.
        """
        return self.annotate(
            num_comments=get_generic_related_count_subquery(
                self.model, Comment
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
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    content = MarkdownField()
    content_tracker = FieldTracker(["content"])

    flags = GenericRelation(Flag, related_query_name="comment")
    likes = GenericRelation(Like, related_query_name="comment")
    notifications = GenericRelation(Notification, related_query_name="comment")

    objects = CommentQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(
                fields=["content_type", "object_id", "owner", "community"]
            )
        ]

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        """
        Returns absolute URL including the community domain.
        """
        return self.community.resolve_url(self.get_absolute_url())

    def get_flags(self) -> models.QuerySet:
        return Flag.objects.filter(comment=self)

    def notify(self, created: bool) -> List[Notification]:
        """
        Creates user notifications:

        - anyone @mentioned in the changed content field
        - anyone subscribed to the comment owner (on create only)
        - the owner of the parent object
        - all community moderators

        Note that the comment owner themselves should never be
        notified of their own comment.
        """
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
