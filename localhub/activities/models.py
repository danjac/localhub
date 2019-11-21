# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
from taggit.models import Tag

from localhub.comments.models import Comment, CommentAnnotationsQuerySetMixin
from localhub.communities.models import Community
from localhub.db.content_types import get_generic_related_queryset
from localhub.db.search import SearchQuerySetMixin
from localhub.db.tracker import Tracker
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.models import Notification
from localhub.utils.text import slugify_unicode


class ActivityQuerySet(
    CommentAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    SearchQuerySetMixin,
    models.QuerySet,
):
    def with_common_annotations(self, user, community):
        """
        Combines commonly used annotations into a single call for
        convenience:
            - with_num_reshares
            - with_num_comments
            - with_num_likes [1]
            - with_has_liked [1]
            - with_has_flagged [1]
            - with_has_reshared [1]
            - with_is_flagged [2]
            [1]: authenticated users only
            [2]: moderators only
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

    def published(self):
        return self.filter(published__isnull=False)

    def published_or_owner(self, user):
        return self.published() | self.filter(owner=user)

    def drafts(self, user):
        return self.filter(published__isnull=True, owner=user)

    def with_num_reshares(self):
        """
        Annotates int value `num_reshares`, indicating how many times
        this activity has been reshared.
        """
        return self.annotate(num_reshares=models.Count("reshares"))

    def with_has_reshared(self, user):
        """
        Annotates boolean value `has_reshared`, indicating if user has
        reshared this activity. If user is anonymous this value will
        always be False.
        """
        if user.is_anonymous:
            return self.annotate(
                has_reshared=models.Value(False, output_field=models.BooleanField())
            )
        return self.annotate(
            has_reshared=models.Exists(
                self.model.objects.filter(parent=models.OuterRef("pk"), owner=user)
            )
        )

    def for_community(self, community):
        """
        Must match community, and owner must also be member.
        """
        return self.filter(
            community=community,
            owner__membership__community=community,
            owner__membership__active=True,
            owner__is_active=True,
        )

    def following_users(self, user):
        """
        Returns instances where the owner of each activity is either followed
        by the user, or is the user themselves. If user is anonymous, then
        passes an unfiltered queryset.
        """

        if user.is_anonymous:
            return self
        return self.filter(owner=user) | self.filter(owner__in=user.following.all())

    def following_tags(self, user):
        """
        Returns instances where each activity either contains tags followed
        by the user, or is owned by user themselves. If user is anonymous, then
        passes an unfiltered queryset.
        """

        if user.is_anonymous:
            return self
        return self.filter(owner=user) | self.filter(tags__in=user.following_tags.all())

    def following(self, user):
        """
        Wraps the methods `following_users` and `following tags`.
        """

        if user.is_anonymous or not user.home_page_filters:
            return self

        qs = self.none()

        if "users" in user.home_page_filters:
            qs = qs | self.following_users(user)

        if "tags" in user.home_page_filters:
            qs = qs | self.following_tags(user)

        return qs

    def without_blocked_users(self, user):
        """
        Excludes any activities of users blocked by this user. If user
        is anonymous then passes unfiltered queryset.
        """

        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

    def without_blocked_tags(self, user):
        """
        Excludes any activities of tags blocked by this user. If user
        is anonymous then passes unfiltered queryset.
        """

        if user.is_anonymous:
            return self
        return self.exclude(
            models.Q(tags__in=user.blocked_tags.all()), ~models.Q(owner=user)
        )

    def without_blocked(self, user):
        """
        Wraps methods `blocked_users` and `blocked_tags`.
        """
        if user.is_anonymous:
            return self
        return self.without_blocked_users(user).without_blocked_tags(user)

    def for_activity_stream(self, user, community):
        """
        Common operations when querying in stream
        """
        return self.with_common_annotations(user, community).select_related(
            "owner", "community", "parent", "parent__owner"
        )


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    RESHARED_FIELDS = ()

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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

    published = DateTimeField(null=True, blank=True)

    history = HistoricalRecords(inherit=True)

    tags = TaggableManager(blank=True)

    search_document = SearchVectorField(null=True, editable=False)

    description_tracker = Tracker(["description"])

    objects = ActivityQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["created", "-created"]),
            models.Index(fields=["published", "-published"]),
        ]
        abstract = True

    @property
    def _history_user(self):
        # used by simple_history
        return self.editor

    @_history_user.setter
    def _history_user(self, value):
        # used by simple_history
        self.editor = value

    def slugify(self):
        return slugify_unicode(self)

    def resolve_url(self, view_name, *args):
        return reverse(
            f"{self._meta.app_label}:{view_name}", args=[self.id] + list(args)
        )

    def get_absolute_url(self):
        if slug := self.slugify():
            return self.resolve_url("detail", slug)
        return self.resolve_url("detail_no_slug")

    def get_create_comment_url(self):
        return self.resolve_url("comment")

    def get_dislike_url(self):
        return self.resolve_url("dislike")

    def get_like_url(self):
        return self.resolve_url("like")

    def get_flag_url(self):
        return self.resolve_url("flag")

    def get_reshare_url(self):
        return self.resolve_url("reshare")

    def get_update_url(self):
        return self.resolve_url("update")

    def get_delete_url(self):
        return self.resolve_url("delete")

    def get_permalink(self):
        return self.community.resolve_url(self.get_absolute_url())

    def get_comments(self):
        return get_generic_related_queryset(self, Comment)

    def get_flags(self):
        return get_generic_related_queryset(self, Flag)

    def get_likes(self):
        return get_generic_related_queryset(self, Like)

    def get_content_warning_tags(self):
        """
        Checks if any tags matching in description
        """
        return (
            self.description.extract_hashtags()
            & self.community.get_content_warning_tags()
        )

    def make_notification(self, recipient, verb, actor=None):
        return Notification(
            content_object=self,
            actor=actor or self.owner,
            community=self.community,
            recipient=recipient,
            verb=verb,
        )

    def notify_mentioned_users(self, recipients):
        qs = recipients.matches_usernames(self.description.extract_mentions()).exclude(
            pk=self.owner_id
        )

        if self.parent:
            qs = qs.exclude(pk=self.parent.owner_id)
        qs = qs.distinct()

        return [self.make_notification(recipient, "mention") for recipient in qs]

    def notify_followers(self, recipients):
        return [
            self.make_notification(follower, "new_followed_user_post")
            for follower in recipients.filter(following=self.owner).distinct()
        ]

    def notify_tag_followers(self, recipients):
        if hashtags := self.description.extract_hashtags():
            tags = Tag.objects.filter(slug__in=hashtags)
            qs = recipients.filter(following_tags__in=tags).exclude(pk=self.owner.id)
            if self.parent:
                qs = qs.exclude(pk=self.parent.owner_id)
            qs = qs.distinct()

            if tags:
                return [
                    self.make_notification(follower, "new_followed_tag_post")
                    for follower in qs
                ]
        return []

    def notify_owner_or_moderators(self):
        """
        Notifies moderators of updates. If change made by moderator,
        then notification sent to owner.
        """
        if self.editor and self.editor != self.owner:
            return [
                self.make_notification(self.owner, "moderator_edit", actor=self.editor)
            ]

        qs = self.community.get_moderators().exclude(pk=self.owner_id)

        if self.parent:
            qs = qs.exclude(pk=self.parent.owner_id)

        qs = qs.distinct()

        return [
            self.make_notification(moderator, "moderator_review_request")
            for moderator in qs
        ]

    def notify_parent_owner(self, recipients):
        if owner := recipients.filter(pk=self.parent.owner_id).first():
            return [self.make_notification(owner, "reshare")]
        return []

    def get_notification_recipients(self):
        return self.community.members.exclude(blocked=self.owner)

    def notify_on_create(self):
        """
        Generates Notification instances for users:
        - @mentioned users
        - users following any tags
        - users following the owner or owner of reshared activity
        - moderators

        Users blocking the owner will not receive notifications.
        """
        notifications = []
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

    def notify_on_update(self):

        notifications = []
        recipients = self.get_notification_recipients()

        if self.description and self.description_tracker.changed():
            notifications += self.notify_mentioned_users(recipients)
            notifications += self.notify_tag_followers(recipients)

        notifications += self.notify_owner_or_moderators()

        Notification.objects.bulk_create(notifications)
        return notifications

    def reshare(self, owner, commit=True, **kwargs):
        """
        Creates a copy of the model.  The subclass must define
        an iterable of `RESHARED_FIELDS`.

        If the activity is already a reshare, a copy is made of the
        *original* model, not the reshare.
        """

        parent = self.parent or self
        reshared = self.__class__(
            owner=owner, is_reshare=True, parent=parent, community=parent.community,
        )
        for field in self.RESHARED_FIELDS:
            setattr(reshared, field, getattr(self, field))
        if commit:
            reshared.save(**kwargs)
        return reshared

    def extract_tags(self, is_new):
        if is_new or self.description_tracker.changed():
            if hashtags := self.description.extract_hashtags():
                self.tags.set(*hashtags, clear=True)
            else:
                self.tags.clear()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        self.extract_tags(is_new)
