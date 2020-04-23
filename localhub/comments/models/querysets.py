# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models

from localhub.bookmarks.models.mixins import BookmarkAnnotationsQuerySetMixin
from localhub.communities.models import Membership
from localhub.db.search.mixins import SearchQuerySetMixin
from localhub.flags.models.mixins import FlagAnnotationsQuerySetMixin
from localhub.likes.models.mixins import LikeAnnotationsQuerySetMixin
from localhub.notifications.models.mixins import NotificationAnnotationsQuerySetMixin

# TBD: break up search into indexer, mixin modules


class CommentQuerySet(
    BookmarkAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    NotificationAnnotationsQuerySetMixin,
    SearchQuerySetMixin,
    models.QuerySet,
):
    def for_community(self, community):
        """
        Both community and membership should match.
        """
        return self.filter(
            community=community,
            owner__membership__community=community,
            owner__membership__active=True,
            owner__is_active=True,
        )

    def with_is_parent_owner_member(self, community):
        return self.annotate(
            is_parent_owner_member=models.Exists(
                Membership.objects.filter(
                    member=models.OuterRef("parent__owner__pk"),
                    community=community,
                    active=True,
                )
            )
        )

    def exclude_blocked_users(self, user):

        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

    def exclude_deleted(self, user=None):
        qs = self.filter(deleted__isnull=True)
        if user:
            qs = qs | self.filter(owner=user)
        return qs

    def with_is_blocked(self, user):
        if user.is_anonymous:
            return self.annotate(
                is_blocked=models.Value(False, output_field=models.BooleanField())
            )
        return self.annotate(
            is_blocked=models.Exists(
                user.blocked.filter(pk=models.OuterRef("owner_id"))
            )
        )

    def with_common_annotations(self, user, community):
        """Combines all common annotations into a single call. Applies annotations
        conditionally e.g. if user is authenticated or not.

        Args:
            user (User)
            community (Community)

        Returns:
            QuerySet
        """

        if user.is_authenticated:
            qs = (
                self.with_num_likes()
                .with_is_new(user)
                .with_has_bookmarked(user)
                .with_has_liked(user)
                .with_has_flagged(user)
                .with_is_blocked(user)
                .with_is_parent_owner_member(community)
            )

            if user.has_perm("communities.moderate_community", community):
                qs = qs.with_is_flagged()
            return qs
        return self

    def with_common_related(self):
        """Include commonly used select_related and prefetch_related fields.

        Returns:
            QuerySet
        """
        return self.select_related(
            "owner", "parent", "community", "parent__owner", "parent__community",
        ).prefetch_related("content_object")

    def deleted(self):
        return self.filter(deleted__isnull=False)

    def remove_content_objects(self):
        """
        Sets content object FKs to NULL.
        """
        return self.update(content_type=None, object_id=None)
