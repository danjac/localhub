# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils import timezone

from model_utils.models import TimeStampedModel

from localhub.bookmarks.models import Bookmark
from localhub.common.db.generic import get_generic_related_queryset
from localhub.common.db.search.indexer import SearchIndexer
from localhub.common.db.tracker import TrackerModelMixin
from localhub.common.markdown.fields import MarkdownField
from localhub.common.utils.itertools import takefirst
from localhub.communities.models import Community
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification

from .managers import CommentManager


class Comment(TrackerModelMixin, TimeStampedModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    edited = models.DateTimeField(null=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    content = MarkdownField()

    search_document = SearchVectorField(null=True, editable=False)

    bookmarks = GenericRelation(Bookmark, related_query_name="comment")
    flags = GenericRelation(Flag, related_query_name="comment")
    likes = GenericRelation(Like, related_query_name="comment")
    notifications = GenericRelation(Notification, related_query_name="comment")

    search_indexer = SearchIndexer(("A", "content"))

    tracked_fields = ["content"]

    objects = CommentManager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created", "-created"]),
        ]

    def __str__(self):
        return self.abbreviate()

    def get_absolute_url(self):
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self):
        """
        Returns absolute URL including the community domain.
        """
        return self.community.resolve_url(self.get_absolute_url())

    def get_notifications(self):
        return get_generic_related_queryset(self, Notification)

    def abbreviate(self, length=30):
        text = " ".join(self.content.plaintext().splitlines())
        return truncatechars(text, length)

    def get_bookmarks(self):
        return Bookmark.objects.filter(comment=self)

    def get_flags(self):
        return Flag.objects.filter(comment=self)

    def get_likes(self):
        return Like.objects.filter(comment=self)

    def soft_delete(self):
        self.deleted = timezone.now()
        self.save(update_fields=["deleted"])

        self.get_likes().delete()
        self.get_flags().delete()
        self.get_notifications().delete()

    def make_notification(self, verb, recipient, actor=None):
        return Notification(
            content_object=self,
            recipient=recipient,
            actor=actor or self.owner,
            community=self.community,
            verb=verb,
        )

    def notify_mentioned(self, recipients):
        return [
            self.make_notification("mention", recipient)
            for recipient in recipients.matches_usernames(
                self.content.extract_mentions()
            ).exclude(pk=self.owner_id)
        ]

    def get_notification_recipients(self):
        return self.community.members.exclude(blocked=self.owner)

    def get_content_object(self):
        """Returns content object; if object is soft deleted, returns None.

        Returns:
            Activity or None
        """
        obj = self.content_object
        if obj and obj.deleted:
            return None
        return obj

    def get_parent(self):
        """Returns parent; if object is soft deleted, returns None.

        Note: if "is_parent_owner_member" annotated attribute is
        present and False will also return None. This attribute
        is annotated with the `with_is_parent_owner_member` QuerySet
        method.

        Returns:
            Comment or None
        """
        if not getattr(self, "is_parent_owner_member", True):
            return None

        obj = self.parent
        if obj and obj.deleted:
            return None
        return obj

    @dispatch
    def notify_on_create(self):
        if (content_object := self.get_content_object()) is None:
            return []

        notifications = []

        recipients = self.get_notification_recipients()
        notifications += self.notify_mentioned(recipients)

        # notify the activity owner
        if self.owner_id != content_object.owner_id:
            notifications += [
                self.make_notification("new_comment", content_object.owner)
            ]

        # notify the person being replied to

        if self.parent:
            notifications += [self.make_notification("reply", self.parent.owner)]

        # notify anyone who has commented on this post, excluding
        # this comment owner and parent owner
        other_commentors = (
            recipients.filter(comment__in=content_object.get_comments())
            .exclude(pk__in=(self.owner_id, content_object.owner_id))
            .distinct()
        )
        if self.parent:
            other_commentors = other_commentors.exclude(pk=self.parent.owner.id)

        notifications += [
            self.make_notification("new_sibling", commentor)
            for commentor in other_commentors
        ]
        notifications += [
            self.make_notification("followed_user", follower)
            for follower in recipients.filter(following=self.owner)
            .exclude(pk__in=other_commentors)
            .distinct()
        ]
        return takefirst(notifications, lambda n: n.recipient)

    @dispatch
    def notify_on_update(self):
        if (self.get_content_object()) is None:
            return []

        if not self.has_tracker_changed():
            return []

        return takefirst(
            self.notify_mentioned(self.get_notification_recipients()),
            lambda n: n.recipient,
        )

    @dispatch
    def notify_on_delete(self, moderator):
        return self.make_notification("delete", self.owner, moderator)
