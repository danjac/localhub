# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional

from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from model_utils.models import TimeStampedModel

from simple_history.models import HistoricalRecords

from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField
from localhub.core.types import BaseQuerySetMixin
from localhub.core.utils.content_types import (
    get_generic_related_count_subquery,
)
from localhub.core.utils.search import SearchIndexer, SearchQuerySetMixin
from localhub.core.utils.tracker import Tracker
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.notifications.models import Notification


class CommentAnnotationsQuerySetMixin(BaseQuerySetMixin):
    """
    Adds comment-related annotation methods to a related model
    queryset.
    """

    def with_num_comments(
        self, annotated_name: str = "num_comments"
    ) -> models.QuerySet:
        """
        Annotates `num_comments` to the model.
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_count_subquery(
                    self.model, Comment
                )
            }
        )


class CommentQuerySet(
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    SearchQuerySetMixin,
    models.QuerySet,
):
    def for_community(self, community: Community) -> models.QuerySet:
        """
        Both community and membership should match.
        """
        return self.filter(community=community, owner__communities=community)

    def blocked_users(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:

        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

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

    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    content = MarkdownField()

    search_document = SearchVectorField(null=True, editable=False)

    flags = GenericRelation(Flag, related_query_name="comment")
    likes = GenericRelation(Like, related_query_name="comment")
    notifications = GenericRelation(Notification, related_query_name="comment")

    history = HistoricalRecords()
    content_tracker = Tracker(["content"])
    search_indexer = SearchIndexer(("A", "content"))

    objects = CommentQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created", "-created"]),
        ]

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        """
        Returns absolute URL including the community domain.
        """
        return self.community.resolve_url(self.get_absolute_url())

    @property
    def _history_user(self) -> Optional[settings.AUTH_USER_MODEL]:
        return self.editor

    @_history_user.setter
    def _history_user(self, value: settings.AUTH_USER_MODEL):
        self.editor = value

    @cached_property
    def first_record(self) -> Optional[models.Model]:
        return self.history.first()

    @cached_property
    def prev_record(self) -> Optional[models.Model]:
        return self.first_record.prev_record if self.first_record else None

    @cached_property
    def changed_fields(self) -> List[str]:
        if self.first_record is None or self.prev_record is None:
            return []
        return self.first_record.diff_against(self.prev_record).changed_fields

    @cached_property
    def has_content_changed(self) -> bool:
        return "content" in self.changed_fields

    def get_flags(self) -> models.QuerySet:
        return Flag.objects.filter(comment=self)

    def make_notification(
        self,
        verb,
        recipient: settings.AUTH_USER_MODEL,
        actor: Optional[settings.AUTH_USER_MODEL] = None,
    ) -> Notification:
        return Notification(
            content_object=self,
            recipient=recipient,
            actor=actor or self.owner,
            community=self.community,
            verb=verb,
        )

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
        recipients = self.community.members.exclude(blocked=self.owner)
        # notify anyone @mentioned in the description
        if self.content and (created or self.content_tracker.changed()):
            notifications += [
                self.make_notification("mention", recipient)
                for recipient in recipients.matches_usernames(  # noqa
                    self.content.extract_mentions()
                ).exclude(pk=self.owner_id)
            ]
        # notify all community moderators
        if (
            self.editor
            and self.editor != self.owner
            and self.owner in recipients
        ):
            notifications += [
                self.make_notification(
                    "moderator_edit", self.owner, self.editor
                )
            ]
        else:
            notifications += [
                self.make_notification("moderator_review_request", recipient)
                for recipient in self.community.get_moderators().exclude(
                    pk=self.owner_id
                )
            ]
        # notify the activity owner
        if created and self.owner_id != self.content_object.owner_id:
            notifications.append(
                self.make_notification(
                    "new_comment", self.content_object.owner
                )
            )
        Notification.objects.bulk_create(notifications)
        return notifications
