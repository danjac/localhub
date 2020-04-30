# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models

from localhub.apps.bookmarks.models import BookmarkAnnotationsQuerySetMixin
from localhub.apps.comments.models import CommentAnnotationsQuerySetMixin
from localhub.apps.flags.models import FlagAnnotationsQuerySetMixin
from localhub.apps.likes.models import LikeAnnotationsQuerySetMixin
from localhub.apps.notifications.models import NotificationAnnotationsQuerySetMixin
from localhub.common.db.search.mixins import SearchQuerySetMixin
from localhub.common.db.utils import boolean_value


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


class ActivityManager(models.Manager.from_queryset(ActivityQuerySet)):
    ...
