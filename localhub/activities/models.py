# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import collections

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
from taggit.models import Tag

from localhub.comments.models import Comment, CommentAnnotationsQuerySetMixin
from localhub.communities.models import Community
from localhub.db.content_types import (
    AbstractGenericRelation,
    get_generic_related_queryset,
)
from localhub.db.search import SearchQuerySetMixin
from localhub.db.tracker import Tracker
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification
from localhub.utils.itertools import takefirst
from localhub.utils.text import slugify_unicode

from .notifications import ActivityNotificationAdapter
from .utils import extract_hashtags


def get_activity_models():
    """
    Returns all Activity subclasses
    """
    return Activity.__subclasses__()


def get_activity_models_dict():
    return {model._meta.model_name: model for model in get_activity_models()}


def get_activity_model(object_type):
    """
    Looks up activity Model for object type string e.g. "post".
    """
    return get_activity_models_dict()[object_type]


def unionize_querysets(querysets, all=False):
    """
    Combines multiple querysets with single UNION statement.
    Columns must all be identical so remember to use with "only()".
    """
    return querysets[0].union(*querysets[1:], all=all)


def load_objects(items, querysets):
    """
    Loads objects from get_activity_querysets() into list of dict:

    union_qs, querysets = get_activity_querysets()
    load_objects(union_qs, querysets)

    [
        {

            "pk": 12345,
            "object_type": "post",
            "object": instance,
        }
    ...
    ]
    """

    bulk_load = collections.defaultdict(set)

    for item in items:
        bulk_load[item["object_type"]].add(item["pk"])

    queryset_dict = {
        queryset.model._meta.model_name: queryset for queryset in querysets
    }

    fetched = {
        (object_type, obj.pk): obj
        for object_type, primary_keys in bulk_load.items()
        for obj in queryset_dict[object_type].filter(pk__in=primary_keys)
    }

    for item in items:
        item["object"] = fetched[(item["object_type"], item["pk"])]

    return items


def get_activity_querysets(queryset_fn, ordering=None, values=None, all=False):
    if isinstance(ordering, str):
        ordering = (ordering,)

    values = list(values) if values else ["pk", "object_type"]

    if ordering:
        values += [field.lstrip("-") for field in ordering]

    querysets = [queryset_fn(model) for model in get_activity_models()]

    qs = unionize_querysets(
        [qs.with_object_type().only(*values).values(*values) for qs in querysets],
        all=all,
    )

    if ordering:
        qs = qs.order_by(*ordering)

    return qs, querysets


def get_activity_queryset_count(queryset_fn):
    querysets = [queryset_fn(model).only("pk") for model in get_activity_models()]
    return unionize_querysets(querysets, all=True).count()


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

        qs = self.with_num_comments(community).with_num_reshares(user, community)
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

    def with_num_reshares(self, user, community):
        """
        Annotates int value `num_reshares`, indicating how many times
        this activity has been reshared.
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

    def with_object_type(self):
        """
        Adds object_type based on model. Useful for generic activity queries.
        """
        return self.annotate(
            object_type=models.Value(
                self.model._meta.model_name, output_field=models.CharField()
            )
        )

    def published(self):
        return self.filter(published__isnull=False)

    def published_or_owner(self, user):
        qs = self.published()
        if user.is_anonymous:
            return qs
        return qs | self.filter(owner=user)

    def drafts(self, user):
        if user.is_anonymous:
            return self.none()
        return self.filter(published__isnull=True, owner=user)

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

    def with_activity_stream_filters(self, user):
        """
        Wraps the methods `following_users` and `following tags`.
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
        """
        Excludes any activities of users blocked by this user. If user
        is anonymous then passes unfiltered queryset.
        """

        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

    def exclude_blocked_tags(self, user):
        """
        Excludes any activities of tags blocked by this user. If user
        is anonymous then passes unfiltered queryset.
        """

        if user.is_anonymous:
            return self
        return self.exclude(
            models.Q(tags__in=user.blocked_tags.all()), ~models.Q(owner=user)
        )

    def exclude_blocked(self, user):
        """
        Wraps methods `blocked_users` and `blocked_tags`.
        """
        if user.is_anonymous:
            return self
        return self.exclude_blocked_users(user).exclude_blocked_tags(user)

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

    RESHARED_FIELDS = ("title", "description")

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

    comments = AbstractGenericRelation(Comment)
    flags = AbstractGenericRelation(Flag)
    likes = AbstractGenericRelation(Like)
    notification = AbstractGenericRelation(Notification)

    history = HistoricalRecords(inherit=True)

    tags = TaggableManager(blank=True)

    search_document = SearchVectorField(null=True, editable=False)

    description_tracker = Tracker(["title", "description"])

    objects = ActivityQuerySet.as_manager()

    notification_adapter_class = ActivityNotificationAdapter

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

    def get_absolute_url(self):
        slug = self.slugify()
        if slug:
            return self.resolve_url("detail", slug)
        return self.resolve_url("detail_no_slug")

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

    def get_create_comment_url(self):
        return self.resolve_url("comment")

    def get_pin_url(self):
        return self.resolve_url("pin")

    def get_unpin_url(self):
        return self.resolve_url("unpin")

    def get_dislike_url(self):
        return self.resolve_url("dislike")

    def get_like_url(self):
        return self.resolve_url("like")

    def get_flag_url(self):
        return self.resolve_url("flag")

    def get_publish_url(self):
        return self.resolve_url("publish")

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

    def get_notifications(self):
        return get_generic_related_queryset(self, Notification)

    def get_content_warning_tags(self):
        """
        Checks if any tags matching in title/description
        """
        return self.extract_tags() & self.community.get_content_warning_tags()

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

    def notify_moderators(self):
        """
        Notifies moderators of updates.
        """

        qs = self.community.get_moderators().exclude(pk=self.owner_id)

        if self.parent:
            qs = qs.exclude(pk=self.parent.owner_id)

        qs = qs.distinct()

        return [
            self.make_notification(moderator, "moderator_review") for moderator in qs
        ]

    def notify_parent_owner(self, recipients):
        owner = recipients.filter(pk=self.parent.owner_id).first()
        if owner:
            return [self.make_notification(owner, "reshare")]
        return []

    def get_notification_recipients(self):
        return self.community.members.exclude(blocked=self.owner)

    @dispatch
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

        notifications += self.notify_moderators()
        return takefirst(notifications, lambda n: n.recipient)

    @dispatch
    def notify_on_update(self):

        notifications = []
        recipients = self.get_notification_recipients()

        if self.description and self.description_tracker.changed():
            notifications += self.notify_mentioned_users(recipients)
            notifications += self.notify_tag_followers(recipients)

        notifications += self.notify_moderators()

        return takefirst(notifications, lambda n: n.recipient)

    def reshare(self, owner, commit=True, **kwargs):
        """
        Creates a copy of the model.  The subclass must define
        an iterable of `RESHARED_FIELDS`.

        If the activity is already a reshare, a copy is made of the
        *original* model, not the reshare.

        Reshares are published immediately, i.e. they do not have a
        "draft mode".
        """

        parent = self.parent or self
        reshared = self.__class__(
            is_reshare=True,
            owner=owner,
            parent=parent,
            community=parent.community,
            **self.get_resharable_data(),
        )

        reshared.published = timezone.now()

        if commit:
            reshared.save(**kwargs)
        return reshared

    def update_reshares(self):
        """
        Sync latest updates with all reshares.
        """
        self.reshares.update(**self.get_resharable_data())

    def get_resharable_data(self):
        return {k: getattr(self, k) for k in self.RESHARED_FIELDS}

    def should_extract_tags(self, is_new):
        return is_new or self.description_tracker.changed()

    def extract_tags(self):
        return self.description.extract_hashtags() | extract_hashtags(self.title)

    def save_tags(self, is_new):
        if self.should_extract_tags(is_new):
            hashtags = self.extract_tags()
            if hashtags:
                self.tags.set(*hashtags, clear=True)
            else:
                self.tags.clear()
