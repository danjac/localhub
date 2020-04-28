# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager
from taggit.models import Tag

from localhub.bookmarks.models import Bookmark
from localhub.comments.models import Comment
from localhub.communities.models import Community
from localhub.db.generic import AbstractGenericRelation, get_generic_related_queryset
from localhub.db.tracker import TrackerModelMixin
from localhub.flags.models import Flag
from localhub.hashtags.fields import HashtagsField
from localhub.hashtags.utils import extract_hashtags
from localhub.likes.models import Like
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification
from localhub.users.fields import MentionsField
from localhub.users.utils import extract_mentions
from localhub.utils.itertools import takefirst
from localhub.utils.text import slugify_unicode

from .. import signals
from .managers import ActivityManager


class Activity(TrackerModelMixin, TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    RESHARED_FIELDS = ["title", "description", "hashtags", "mentions"]

    INDEXABLE_DESCRIPTION_FIELDS = [
        "description",
        "hashtags",
        "mentions",
    ]

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

    # using "hashtags" so not to confuse with "tags" M2M field
    hashtags = HashtagsField(max_length=300, blank=True)

    mentions = MentionsField(max_length=300, blank=True)

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

    tags = TaggableManager(blank=True)

    search_document = SearchVectorField(null=True, editable=False)

    tracked_fields = ["title", "description", "hashtags", "mentions"]

    objects = ActivityManager()

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

    @property
    def indexable_description(self):
        """Returns default indexable description fields for search trackers.
        """
        return " ".join(
            [
                value
                for value in [
                    getattr(self, field, "")
                    for field in self.INDEXABLE_DESCRIPTION_FIELDS
                ]
                if value
            ]
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
        hashtags = self.extract_hashtags()
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
    def notify_on_publish(self):
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

    def hashtags_changed(self):
        return self.has_tracker_changed(["title", "description", "hashtags"])

    def mentions_changed(self):
        return self.has_tracker_changed(["title", "description", "mentions"])

    @dispatch
    def notify_on_update(self):
        """Notifies mentioned users and tag followers if content changed.

        Returns:
            list: Notification instances
        """
        notifications = []
        recipients = self.get_notification_recipients()

        if self.mentions_changed():
            notifications += self.notify_mentioned_users(recipients)

        if self.hashtags_changed():
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
            | self.mentions.extract_mentions()
            | extract_mentions(self.title)
        )

    def should_extract_hashtags(self, is_new):
        return is_new or self.hashtags_changed()

    def extract_hashtags(self):
        return (
            self.description.extract_hashtags()
            | self.hashtags.extract_hashtags()
            | extract_hashtags(self.title)
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
