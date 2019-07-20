# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from functools import reduce
from typing import Callable, Dict, List, Optional, Set

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel

from simple_history.models import HistoricalRecords

from taggit.managers import TaggableManager
from taggit.models import Tag

from localhub.comments.models import Comment, CommentAnnotationsQuerySetMixin
from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField
from localhub.core.types import BreadcrumbList
from localhub.core.utils.content_types import get_generic_related_queryset
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.notifications.models import Notification
from localhub.subscriptions.models import Subscription


class ActivityQuerySet(
    CommentAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    models.QuerySet,
):
    def with_common_annotations(
        self, community: Community, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        """
        Combines all common annotations into a single call. Applies annotations
        conditionally e.g. if user is authenticated or not.
        """

        qs = self.with_num_comments()
        if user.is_authenticated:
            qs = (
                qs.with_num_likes().with_has_liked(user).with_has_flagged(user)
            )

            if user.has_perm("communities.moderate_community", community):
                qs = qs.with_is_flagged()
        return qs

    def following(self, user: settings.AUTH_USER_MODEL) -> models.QuerySet:
        """
        Includes only instances where the activity owner is subscribed by
        the user.
        """
        return self.filter(
            models.Q(owner__subscriptions__subscriber=user)
            | models.Q(owner=user)
        )

    def search(self, search_term: str) -> models.QuerySet:
        """
        Returns result of search on indexed fields. Annotates with
        `rank` to allow ordering by search result accuracy.
        """
        if not search_term:
            return self.none()
        query = SearchQuery(search_term)
        return self.annotate(
            rank=SearchRank(models.F("search_document"), query=query)
        ).filter(search_document=query)


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    description = MarkdownField(blank=True)

    history = HistoricalRecords(inherit=True)

    tags = TaggableManager()

    search_document = SearchVectorField(null=True, editable=False)

    objects = ActivityQuerySet.as_manager()

    # Note: due to bug in FieldTracker we can't define it in abstract base
    # class and have to define on each subclass.
    # https://github.com/jazzband/django-model-utils/issues/275

    # add following to all Activity subclasses in order to track
    # description for notifications etc.
    # description_tracker = FieldTracker(["description"])

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["owner", "community"]),
        ]
        abstract = True

    @classmethod
    def get_list_url(cls) -> str:
        """
        Returns the default list view URL of the model.
        """
        return reverse(f"{cls._meta.app_label}:list")

    @classmethod
    def get_create_url(cls) -> str:
        """
        Returns the default create view URL of the model.
        """
        return reverse(f"{cls._meta.app_label}:create")

    @classmethod
    def get_breadcrumbs_for_model(cls) -> BreadcrumbList:
        """
        Creates a default breadcrumb navigation for the model class.
        """
        return [
            (settings.HOME_PAGE_URL, _("Home")),
            (cls.get_list_url(), _(cls._meta.verbose_name_plural.title())),
        ]

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

    @cached_property
    def editor(self) -> Optional[settings.AUTH_USER_MODEL]:
        try:
            return (
                self.history.select_related("history_user")
                .latest()
                .history_user
            )
        except ObjectDoesNotExist:
            return None

    def is_moderated(self) -> bool:
        return self.editor is not None and self.editor != self.owner

    def get_breadcrumbs(self) -> BreadcrumbList:
        """
        Returns breadcrumb navigation for individual instance.
        """
        return self.__class__.get_breadcrumbs_for_model() + [
            (self.get_absolute_url(), truncatechars(smart_text(self), 60))
        ]

    def get_content_warning_tags(self) -> Set[str]:
        """
        Checks if any tags matching in description
        """
        return (
            self.description.extract_hashtags()
            & self.community.get_content_warning_tags()
        )

    def search_index_components(self) -> Dict[str, str]:
        """
        Return a dict of text elements for inclusion in the search document.
        Dict keys should be A, B, C and so forth depending on weighting.

        e.g.

        {"A": self.title, "B": self.description}
        """
        return {}

    def make_search_updater(self) -> Callable:
        """
        Returns an indexing function to update the PostgreSQL search document
        for this instance.

        In post_save signal:

        transaction.on_commit(instance.make_search_updater())
        """

        def on_commit():
            search_vectors = [
                SearchVector(
                    models.Value(text, output_field=models.CharField()),
                    weight=weight,
                )
                for (weight, text) in self.search_index_components().items()
            ]
            self.__class__.objects.filter(pk=self.pk).update(
                search_document=reduce(operator.add, search_vectors)
            )

        return on_commit

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

    def notify_mentioned_users(self) -> List[Notification]:
        return [
            self.make_notification(recipient, "mentioned")
            for recipient in self.community.members.matches_usernames(
                self.description.extract_mentions()
            ).exclude(pk=self.owner_id)
        ]

    def notify_followers(self) -> List[Notification]:
        subscriptions = (
            Subscription.objects.filter(
                user=self.owner, community=self.community
            )
            .exclude(subscriber=self.owner)
            .select_related("subscriber")
        )
        return [
            self.make_notification(subscription.subscriber, "created")
            for subscription in subscriptions
        ]

    def notify_tag_subscribers(self) -> List[Notification]:
        hashtags = self.description.extract_hashtags()
        if hashtags:
            tags = Tag.objects.filter(slug__in=hashtags)

            if tags:
                subscriptions = (
                    Subscription.objects.filter(
                        content_type=ContentType.objects.get_for_model(Tag),
                        object_id__in=[t.id for t in tags],
                        community=self.community,
                    )
                    .exclude(subscriber=self.owner)
                    .select_related("subscriber")
                    .only("subscriber")
                )
                return [
                    self.make_notification(subscriber, "tagged")
                    for subscriber in set(
                        [
                            subscription.subscriber
                            for subscription in subscriptions
                        ]
                    )
                ]
        return []

    def notify_owner_or_moderators(
        self, created: bool, editor: Optional[settings.AUTH_USER_MODEL] = None
    ) -> List[Notification]:
        """
        Notifies moderators of updates. If change made by moderator,
        then notification sent to owner.
        """
        verb = "created" if created else "updated"

        if editor and editor != self.owner:
            return [
                self.make_notification(self.owner, "moderated", actor=editor)
            ]
        return [
            self.make_notification(moderator, verb)
            for moderator in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]

    def notify(
        self, created: bool, editor: Optional[settings.AUTH_USER_MODEL] = None
    ) -> List[Notification]:
        """
        Generates user notifications when instance is created
        or updated.

        The following notifications may be created:

        - any users @mentioned in the description field
        - any users subscribed to hashtags in the description field
        - any users subscribed to the owner (only on create)
        - if moderated, the original owner
        """
        notifications: List[Notification] = []
        if self.description and (
            created or self.description_tracker.changed()
        ):
            notifications += self.notify_mentioned_users()
            notifications += self.notify_tag_subscribers()

        if created:
            notifications += self.notify_followers()

        notifications += self.notify_owner_or_moderators(created, editor)

        Notification.objects.bulk_create(notifications)
        return notifications
