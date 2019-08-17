# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from typing import Iterable, List, Optional, Set

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify

from model_utils.models import TimeStampedModel

from simple_history.models import HistoricalRecords

from taggit.managers import TaggableManager
from taggit.models import Tag

from localhub.comments.models import Comment, CommentAnnotationsQuerySetMixin
from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField
from localhub.core.utils.content_types import get_generic_related_queryset
from localhub.core.utils.search import SearchQuerySetMixin
from localhub.core.utils.tracker import Tracker
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.notifications.models import Notification


class ActivityQuerySet(
    CommentAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    SearchQuerySetMixin,
    models.QuerySet,
):
    def with_common_annotations(
        self, community: Community, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        """
        Combines all common annotations into a single call. Applies annotations
        conditionally e.g. if user is authenticated or not.
        """

        qs = self.with_num_comments().with_num_reshares()
        if user.is_authenticated:
            qs = (
                qs.with_num_likes()
                .with_has_liked(user)
                .with_has_flagged(user)
                .with_has_reshared(user)
            )

            if user.has_perm("communities.moderate_community", community):
                qs = qs.with_is_flagged()
        return qs

    def with_num_reshares(self) -> models.QuerySet:
        return self.annotate(num_reshares=models.Count("reshares"))

    def with_has_reshared(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        if user.is_anonymous:
            return self.annotate(
                has_reshared=models.Value(
                    False, output_field=models.BooleanField()
                )
            )
        return self.annotate(
            has_reshared=models.Exists(
                self.model.objects.filter(
                    parent=models.OuterRef("pk"), owner=user
                )
            )
        )

    def for_community(self, community: Community) -> models.QuerySet:
        """
        Must match community, and owner must also be member.
        """
        return self.filter(community=community, owner__communities=community)

    def following_users(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:

        if user.is_anonymous:
            return self
        return self.filter(owner=user) | self.filter(
            owner__in=user.following.all()
        )

    def following_tags(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:

        if user.is_anonymous:
            return self
        return self.filter(owner=user) | self.filter(
            tags__in=user.following_tags.all()
        )

    def following(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:

        if user.is_anonymous or not user.home_page_filters:
            return self

        qs = self.none()

        if "users" in user.home_page_filters:
            qs = qs | self.following_users(user)

        if "tags" in user.home_page_filters:
            qs = qs | self.following_tags(user)

        return qs

    def blocked_users(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:

        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

    def blocked_tags(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:
        """
        Should remove all activities with tags except if user is owner
        """
        if user.is_anonymous:
            return self
        return self.exclude(
            models.Q(tags__in=user.blocked_tags.all()), ~models.Q(owner=user)
        )

    def blocked(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:
        if user.is_anonymous:
            return self
        return self.blocked_users(user).blocked_tags(user)


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    RESHARED_FIELDS: Iterable = ()

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

    description = MarkdownField(blank=True)

    allow_comments = models.BooleanField(default=True)

    is_reshare = models.BooleanField(default=False)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="reshares",
        on_delete=models.SET_NULL,
    )

    history = HistoricalRecords(inherit=True)

    tags = TaggableManager(blank=True)

    search_document = SearchVectorField(null=True, editable=False)

    description_tracker = Tracker(["description"])

    objects = ActivityQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["created", "-created"]),
        ]
        abstract = True

    @property
    def _history_user(self) -> Optional[settings.AUTH_USER_MODEL]:
        return self.editor

    @_history_user.setter
    def _history_user(self, value: settings.AUTH_USER_MODEL):
        self.editor = value

    def slugify(self) -> str:
        return slugify(smart_text(self), allow_unicode=False)

    def resolve_url(self, view_name: str, *args) -> str:
        return reverse(
            f"{self._meta.app_label}:{view_name}", args=[self.id] + list(args)
        )

    def get_absolute_url(self) -> str:
        return self.resolve_url("detail", self.slugify())

    def get_create_comment_url(self) -> str:
        return self.resolve_url("comment")

    def get_dislike_url(self) -> str:
        return self.resolve_url("dislike")

    def get_like_url(self) -> str:
        return self.resolve_url("like")

    def get_flag_url(self) -> str:
        return self.resolve_url("flag")

    def get_reshare_url(self) -> str:
        return self.resolve_url("reshare")

    def get_update_url(self) -> str:
        return self.resolve_url("update")

    def get_delete_url(self) -> str:
        return self.resolve_url("delete")

    def get_permalink(self) -> str:
        return self.community.resolve_url(self.get_absolute_url())

    def get_comments(self) -> models.QuerySet:
        return get_generic_related_queryset(self, Comment)

    def get_flags(self) -> models.QuerySet:
        return get_generic_related_queryset(self, Flag)

    def get_likes(self) -> models.QuerySet:
        return get_generic_related_queryset(self, Like)

    def get_content_warning_tags(self) -> Set[str]:
        """
        Checks if any tags matching in description
        """
        return (
            self.description.extract_hashtags()
            & self.community.get_content_warning_tags()
        )

    def taggit(self, created: bool):
        """
        Generates Tag instances from #hashtags in the description field when
        changed. Pre-existing tags are deleted.
        """
        if created or self.description_tracker.changed():
            hashtags = self.description.extract_hashtags()
            if hashtags:
                self.tags.set(*hashtags, clear=True)
            else:
                self.tags.clear()

    def make_notification(
        self,
        recipient: settings.AUTH_USER_MODEL,
        verb: str,
        actor: Optional[settings.AUTH_USER_MODEL] = None,
    ) -> Notification:
        return Notification(
            content_object=self,
            actor=actor or self.owner,
            community=self.community,
            recipient=recipient,
            verb=verb,
        )

    def notify_mentioned_users(
        self, recipients: models.QuerySet
    ) -> List[Notification]:
        qs = recipients.matches_usernames(
            self.description.extract_mentions()
        ).exclude(pk=self.owner_id)

        if self.parent:
            qs = qs.exclude(pk=self.parent.owner_id)
        qs = qs.distinct()

        return [
            self.make_notification(recipient, "mention") for recipient in qs
        ]

    def notify_followers(
        self, recipients: models.QuerySet
    ) -> List[Notification]:
        return [
            self.make_notification(follower, "new_followed_user_post")
            for follower in recipients.filter(following=self.owner).distinct()
        ]

    def notify_tag_followers(
        self, recipients: models.QuerySet
    ) -> List[Notification]:
        hashtags = self.description.extract_hashtags()
        if hashtags:
            tags = Tag.objects.filter(slug__in=hashtags)
            qs = recipients.filter(following_tags__in=tags).exclude(
                pk=self.owner.id
            )
            if self.parent:
                qs = qs.exclude(pk=self.parent.owner_id)
            qs = qs.distinct()

            if tags:
                return [
                    self.make_notification(follower, "new_followed_tag_post")
                    for follower in qs
                ]
        return []

    def notify_owner_or_moderators(self) -> List[Notification]:
        """
        Notifies moderators of updates. If change made by moderator,
        then notification sent to owner.
        """
        if self.editor and self.editor != self.owner:
            return [
                self.make_notification(
                    self.owner, "moderator_edit", actor=self.editor
                )
            ]

        qs = self.community.get_moderators().exclude(pk=self.owner_id)

        if self.parent:
            qs = qs.exclude(pk=self.parent.owner_id)

        qs = qs.distinct()

        return [
            self.make_notification(moderator, "moderator_review_request")
            for moderator in qs
        ]

    def notify_parent_owner(
        self, recipients: models.QuerySet
    ) -> List[Notification]:
        owner = recipients.filter(pk=self.parent.owner_id).first()
        if owner:
            return [self.make_notification(owner, "reshare")]
        return []

    def get_notification_recipients(self) -> models.QuerySet:
        return self.community.members.exclude(blocked=self.owner)

    def notify_on_create(self) -> List[Notification]:
        notifications: List[Notification] = []
        recipients = self.get_notification_recipients()

        if self.description:
            notifications += self.notify_mentioned_users(recipients)
            notifications += self.notify_tag_followers(recipients)

        notifications += self.notify_followers(recipients)

        if self.parent:
            notifications += self.notify_parent_owner(recipients)

        notifications += self.notify_owner_or_moderators()

        Notification.objects.bulk_create(notifications)
        return notifications

    def notify_on_update(self) -> List[Notification]:

        notifications: List[Notification] = []
        recipients = self.get_notification_recipients()

        if self.description and self.description_tracker.changed():
            notifications += self.notify_mentioned_users(recipients)
            notifications += self.notify_tag_followers(recipients)

        notifications += self.notify_owner_or_moderators()

        Notification.objects.bulk_create(notifications)
        return notifications

    def reshare(
        self, owner: settings.AUTH_USER_MODEL, commit=True, **kwargs
    ) -> models.Model:
        """
        Creates a copy of the model.  The subclass must define
        an iterable of `RESHARED_FIELDS`.

        If the activity is already a reshare, a copy is made of the
        *original* model, not the reshare.
        """

        parent = self.parent or self
        reshared = self.__class__(
            owner=owner,
            is_reshare=True,
            parent=parent,
            community=parent.community,
        )
        for field in self.RESHARED_FIELDS:
            setattr(reshared, field, getattr(self, field))
        if commit:
            reshared.save(**kwargs)
        return reshared
