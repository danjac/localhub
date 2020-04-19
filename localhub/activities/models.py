# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
from taggit.models import Tag

from localhub.bookmarks.models import Bookmark, BookmarkAnnotationsQuerySetMixin
from localhub.comments.models import Comment, CommentAnnotationsQuerySetMixin
from localhub.communities.models import Community
from localhub.db.content_types import (
    AbstractGenericRelation,
    get_generic_related_queryset,
)
from localhub.db.search import SearchQuerySetMixin
from localhub.db.tracker import Tracker
from localhub.db.utils import boolean_value
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.hashtags.utils import extract_hashtags
from localhub.hashtags.validators import validate_hashtags
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import (
    Notification,
    NotificationAnnotationsQuerySetMixin,
)
from localhub.users.utils import extract_mentions
from localhub.users.validators import validate_mentions
from localhub.utils.itertools import takefirst
from localhub.utils.text import slugify_unicode

from . import signals


class ActivityQuerySet(
    BookmarkAnnotationsQuerySetMixin,
    CommentAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    NotificationAnnotationsQuerySetMixin,
    SearchQuerySetMixin,
    models.QuerySet,
):
    def with_common_annotations(self, user, community):
        """Combines commonly used annotations into a single call for
        convenience:
            - with_num_reshares
            - with_num_comments
            - with_num_likes
            - with_is_new [1]
            - with_has_liked [1]
            - with_has_bookmarked [1]
            - with_has_flagged [1]
            - with_has_reshared [1]
            - with_is_flagged [2]
            [1]: authenticated users only
            [2]: moderators only

        Args:
            user (User): the current user
            community (Community)

        Returns:
            QuerySet
        """

        qs = self.with_num_comments(community).with_num_reshares(user, community)
        if user.is_authenticated:
            qs = (
                qs.with_num_likes()
                .with_is_new(user)
                .with_has_bookmarked(user)
                .with_has_liked(user)
                .with_has_flagged(user)
                .with_has_reshared(user)
            )

            if user.has_perm("communities.moderate_community", community):
                qs = qs.with_is_flagged()
        return qs

    def with_num_reshares(self, user, community):
        """Annotates int value `num_reshares`, indicating how many times
        this activity has been reshared.

        Args:
            user (User): the current user
            community (Community)

        Returns:
            QuerySet
        """
        return self.annotate(
            num_reshares=models.Subquery(
                self.model.objects.filter(parent=models.OuterRef("pk"))
                .for_community(community)
                .exclude_blocked_users(user)
                .values("parent")
                .annotate(count=models.Count("pk"))
                .values("count"),
                output_field=models.IntegerField(),
            )
        )

    def exists_reshares(self, user):
        """Returns expression if user exists.

        Args:
            user (User)

        Returns:
            Exists
        """
        return models.Exists(
            self.model.objects.filter(parent=models.OuterRef("pk"), owner=user)
        )

    def unreshared(self, user):
        """Returns QuerySet of activities not reshared by this user.

        Args:
            user (User): the current user

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self
        return self.filter(~self.exists_reshares(user))

    def with_has_reshared(self, user):
        """Annotates boolean value `has_reshared`, indicating if user has
        reshared this activity. If user is anonymous this value will
        always be False.

        Args:
            user (User): the current user

        Returns:
            QuerySet
         """
        return self.annotate(
            has_reshared=boolean_value(False)
            if user.is_anonymous
            else self.exists_reshares(user)
        )

    def with_object_type(self):
        """Adds object_type based on model. Useful for generic activity queries.

        Returns:
            QuerySet
        """
        return self.annotate(
            object_type=models.Value(
                self.model._meta.model_name, output_field=models.CharField()
            )
        )

    def published(self):
        """Filter activities that have been published i.e. published is NOT NULL.

        Returns:
            QuerySet
        """
        return self.filter(published__isnull=False, deleted__isnull=True)

    def deleted(self):
        """Returns activities deleted by moderator vs. "hard-deleted" i.e.
        deleted is NOT NULL.

        Returns:
            QuerySet
        """
        return self.filter(deleted__isnull=False)

    def published_or_owner(self, user):
        """Returns activities either made public (published NOT NULL) or where
        user is the owner.

        Args:
            user (User): current user. If anonymous just returns public activities.

        Returns:
            QuerySet
        """
        qs = self.published()
        if user.is_anonymous:
            return qs
        return qs | self.filter(owner=user)

    def private(self, user):
        """Returns activities not yet made public (published NULL) belonging to this
        user.

        Args:
            user (User): current user. If anonymous just returns empty QuerySet.

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self.none()
        return self.filter(published__isnull=True, deleted__isnull=True, owner=user)

    def for_community(self, community):
        """Must match community, and owners must also be active members.

        Args:
            community (Community)

        Returns:
            QuerySet
        """
        return self.filter(
            community=community,
            owner__membership__community=community,
            owner__membership__active=True,
            owner__is_active=True,
        )

    def following_users(self, user):
        """Returns instances where the owner of each activity is either followed
        by the user, or is the user themselves. If user is anonymous, then
        passes an unfiltered queryset.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self
        return self.filter(owner=user) | self.filter(owner__in=user.following.all())

    def following_tags(self, user):
        """Returns instances where each activity either contains tags followed
        by the user, or is owned by user themselves. If user is anonymous, then
        passes an unfiltered queryset.

        Args:
            user (User)

        Returns:
            QuerySet
        """

        if user.is_anonymous:
            return self
        return self.filter(owner=user) | self.filter(tags__in=user.following_tags.all())

    def with_activity_stream_filters(self, user):
        """
        Wraps the methods `following_users` and `following tags`. Used in common
        activity stream views.

        Args:
            user (User)

        Returns:
            QuerySet
        """

        if user.is_anonymous or not user.activity_stream_filters:
            return self

        qs = self.none()

        if "users" in user.activity_stream_filters:
            qs = qs | self.following_users(user)

        if "tags" in user.activity_stream_filters:
            qs = qs | self.following_tags(user)

        return qs

    def exclude_blocked_users(self, user):
        """Excludes any activities of users blocked by this user. If user
        is anonymous then passes unfiltered queryset.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

    def exclude_blocked_tags(self, user):
        """Excludes any activities of tags blocked by this user. If user
        is anonymous then passes unfiltered queryset.

        Args:
            user (User)

        Returns:
            QuerySet
        """

        if user.is_anonymous:
            return self
        return self.exclude(
            models.Q(tags__in=user.blocked_tags.all()), ~models.Q(owner=user)
        )

    def exclude_blocked(self, user):
        """Wraps methods `blocked_users` and `blocked_tags`.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        if user.is_anonymous:
            return self
        return self.exclude_blocked_users(user).exclude_blocked_tags(user)

    def for_activity_stream(self, user, community):
        """Common operations when querying in stream

        Args:
            user (User)
            community (Community)

        Returns:
            QuerySet
        """
        return self.with_common_annotations(user, community).select_related(
            "owner", "community", "parent", "parent__owner"
        )


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    RESHARED_FIELDS = ("title", "description", "additional_tags")

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    title = models.CharField(max_length=300)

    # using "additional_tags" so not to confuse with "tags" M2M field
    additional_tags = models.CharField(
        max_length=300, blank=True, validators=[validate_hashtags]
    )

    mentions = models.CharField(
        max_length=300, blank=True, validators=[validate_mentions]
    )

    description = MarkdownField(blank=True)

    allow_comments = models.BooleanField(default=True)

    is_reshare = models.BooleanField(default=False)

    is_pinned = models.BooleanField(default=False)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="reshares",
        on_delete=models.SET_NULL,
    )

    edited = models.DateTimeField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)

    # NOTE: not adding comments here as we don't want comments
    # to be soft deleted.
    bookmarks = AbstractGenericRelation(Bookmark)
    flags = AbstractGenericRelation(Flag)
    likes = AbstractGenericRelation(Like)
    notification = AbstractGenericRelation(Notification)

    history = HistoricalRecords(inherit=True)

    tags = TaggableManager(blank=True)

    search_document = SearchVectorField(null=True, editable=False)

    hashtags_tracker = Tracker(["title", "description", "additional_tags"])
    mentions_tracker = Tracker(["title", "description", "mentions"])

    objects = ActivityQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["created", "-created"]),
            models.Index(fields=["published", "-published"]),
        ]
        abstract = True

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        self.save_tags(is_new)

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
        """Resolves URL for a specific action depending on the
        type of Activity subclass. The PK is prepended in all cases.

        Example:

        post.resolve_url("delete") -> /posts/1234/~delete/

        See localhub/activities/urls/generic.py for list of common
        activity actions.

        Args:
            view_name (str): base view name e.g. "delete" or "like"
            *args: additional arguments for the URL

        Returns:
            str: specific URL endpoint of action.
        """
        return reverse(
            f"{self._meta.app_label}:{view_name}", args=[self.id] + list(args)
        )

    def get_absolute_url(self):
        slug = self.slugify()
        if slug:
            return self.resolve_url("detail", slug)
        return self.resolve_url("detail_no_slug")

    def get_permalink(self):
        """
        Returns:
            str: absolute URL of object including full path of community.
        """
        return self.community.resolve_url(self.get_absolute_url())

    def get_comments(self):
        """
        Returns:
            QuerySet: Comments belonging to Activity instance.
        """
        return get_generic_related_queryset(self, Comment)

    def get_flags(self):
        """
        Returns:
            QuerySet: Flags belonging to Activity instance.
        """
        return get_generic_related_queryset(self, Flag)

    def get_bookmarks(self):
        """
        Returns:
            QuerySet: Bookmarks belonging to Activity instance.
        """
        return get_generic_related_queryset(self, Bookmark)

    def get_likes(self):
        """
        Returns:
            QuerySet: Likes belonging to Activity instance.
        """
        return get_generic_related_queryset(self, Like)

    def get_notifications(self):
        """
        Returns:
            QuerySet: Notifications belonging to Activity instance.
        """
        return get_generic_related_queryset(self, Notification)

    def get_content_warning_tags(self):
        """Checks if any tags matching in title/description/additional
        tags etc that match the warning tags for this community.

        Returns:
            set: tag strings
        """
        return self.extract_hashtags() & self.community.get_content_warning_tags()

    def is_content_sensitive(self, user):
        """
        Returns True if activity content includes any community-defined
        warning tags, unless:
            1. User is the owner
            2. User has selected to show sensitive content
        Args:
            user (User)

        Returns:
            bool
        """
        if user.is_authenticated and user.show_sensitive_content:
            return False
        if self.owner == user:
            return False
        return bool(self.get_content_warning_tags())

    def make_notification(self, recipient, verb, actor=None):
        return Notification(
            content_object=self,
            actor=actor or self.owner,
            community=self.community,
            recipient=recipient,
            verb=verb,
        )

    def notify_mentioned_users(self, recipients):
        qs = recipients.matches_usernames(self.extract_mentions()).exclude(
            pk=self.owner_id
        )

        if self.editor:
            qs = qs.exclude(pk=self.editor.id)

        if self.parent:
            qs = qs.exclude(pk=self.parent.owner_id)
        qs = qs.distinct()

        return [self.make_notification(recipient, "mention") for recipient in qs]

    def notify_followers(self, recipients):
        qs = recipients.filter(following=self.owner).distinct()

        if self.editor:
            qs = qs.exclude(pk=self.editor.id)

        return [self.make_notification(follower, "followed_user") for follower in qs]

    def notify_tag_followers(self, recipients):
        hashtags = self.description.extract_hashtags()
        if hashtags:
            tags = Tag.objects.filter(slug__in=hashtags)
            qs = recipients.filter(following_tags__in=tags).exclude(pk=self.owner.id)

            if self.editor:
                qs = qs.exclude(pk=self.editor.id)

            if self.parent:
                qs = qs.exclude(pk=self.parent.owner_id)

            qs = qs.distinct()

            if tags:
                return [
                    self.make_notification(follower, "followed_tag") for follower in qs
                ]
        return []

    def notify_parent_owner(self, recipients):
        owner = recipients.filter(pk=self.parent.owner_id).first()
        if owner:
            return [self.make_notification(owner, "reshare")]
        return []

    def get_notification_recipients(self):
        return self.community.members.exclude(blocked=self.owner)

    @dispatch
    def notify_on_create(self):
        """Generates Notification instances for users:
        - @mentioned users
        - users following any tags
        - users following the owner or owner of reshared activity
        - moderators

        Users blocking the owner will not receive notifications.

        Returns:
            list: Notification instances
        """
        notifications = []
        recipients = self.get_notification_recipients()

        if self.parent:
            notifications += self.notify_parent_owner(recipients)

        if self.description:
            notifications += self.notify_mentioned_users(recipients)
            notifications += self.notify_tag_followers(recipients)

        notifications += self.notify_followers(recipients)

        return takefirst(notifications, lambda n: n.recipient)

    def notify_owner_on_edit(self):
        return self.make_notification(self.owner, "edit", actor=self.editor)

    @dispatch
    def notify_on_update(self):
        """Notifies mentioned users and tag followers if content changed.

        Returns:
            list: Notification instances
        """
        notifications = []
        recipients = self.get_notification_recipients()

        if self.mentions_tracker.changed():
            notifications += self.notify_mentioned_users(recipients)

        if self.hashtags_tracker.changed():
            notifications += self.notify_tag_followers(recipients)

        if self.editor and self.editor != self.owner:
            notifications.append(self.notify_owner_on_edit())

        return takefirst(notifications, lambda n: n.recipient)

    @dispatch
    def notify_on_delete(self, moderator):
        """Notifies owner if object has been deleted by moderator.

        Args:
            moderator (User): moderator who has "soft deleted" the object

        Returns:
            Notification
        """
        return self.make_notification(self.owner, "delete", actor=moderator)

    def reshare(self, owner, commit=True, **kwargs):
        """Creates a copy of the model. The fields to be shared are
        defined under RESHARED_FIELDS.

        If the activity is already a reshare, a copy is made of the
        *original* model, not the reshare.

        Reshares are published immediately, i.e. they do not have a
        "private mode".

        Args:
            owner (User): owner creating the reshare
            commit (bool, optional): commit new reshare to database (default: True)
            **kwargs: keyword args passed to save() method of reshared instance.

        Returns:
            reshared copy of the Activity subclass instance
        """

        parent = self.parent or self
        reshared = self.__class__(
            is_reshare=True,
            owner=owner,
            parent=parent,
            community=parent.community,
            published=timezone.now(),
            **self.get_resharable_data(),
        )

        if commit:
            reshared.save(**kwargs)
        return reshared

    def update_reshares(self):
        """Sync latest updates with all reshares.
        """
        self.reshares.update(**self.get_resharable_data())

    @transaction.atomic
    def soft_delete(self):
        """Moderators "soft delete" an activity rather than delete it completely.
        The published field is also set to NULL.

        Comments and reshares are not deleted.

        Notifications, bookmarks, flags and likes should be deleted
        (there may be subsequent notification i.e. to notify the owner).

        Fires the "soft_delete" signal.
        """
        self.deleted = timezone.now()
        self.published = None
        self.save(update_fields=["deleted", "published"])

        self.get_comments().remove_content_objects()

        self.get_bookmarks().delete()
        self.get_likes().delete()
        self.get_flags().delete()
        self.get_notifications().delete()

        signals.soft_delete.send(sender=self.__class__, instance=self)

    def get_resharable_data(self):
        return {k: getattr(self, k) for k in self.RESHARED_FIELDS}

    def extract_mentions(self):
        return (
            self.description.extract_mentions()
            | extract_mentions(self.title)
            | extract_mentions(self.mentions)
        )

    def should_extract_hashtags(self, is_new):
        return is_new or self.hashtags_tracker.changed()

    def extract_hashtags(self):
        return (
            self.description.extract_hashtags()
            | extract_hashtags(self.title)
            | extract_hashtags(self.additional_tags)
        )

    def save_tags(self, is_new):
        if self.should_extract_hashtags(is_new):
            hashtags = self.extract_hashtags()
            if hashtags:
                self.tags.set(*hashtags, clear=True)
            else:
                self.tags.clear()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """Comment relations should be set to NULL. Django GenericRelation
        for whatever weird and wonderful reason does not support this.
        """
        self.get_comments().remove_content_objects()
        return super().delete(*args, **kwargs)
