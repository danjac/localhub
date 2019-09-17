# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from localhub.activities.models import Activity, ActivityQuerySet
from localhub.comments.models import Comment
from localhub.common.db.search import SearchIndexer
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification


class PollQuerySet(ActivityQuerySet):
    def with_voting_counts(self):
        return self.prefetch_related(
            models.Prefetch(
                "answers",
                queryset=Answer.objects.annotate(
                    num_votes=models.Count("voters", distinct=True)
                ).order_by("id"),
            )
        ).annotate(
            total_num_votes=models.Count("answers__voters", distinct=True)
        )

    def for_activity_stream(self, user, community):
        return (
            super().for_activity_stream(user, community).with_voting_counts()
        )


class Poll(Activity):
    RESHARED_FIELDS = ("title", "description")

    title = models.CharField(max_length=300)
    comments = GenericRelation(Comment, related_query_name="poll")
    flags = GenericRelation(Flag, related_query_name="poll")
    likes = GenericRelation(Like, related_query_name="poll")
    notifications = GenericRelation(Notification, related_query_name="poll")

    search_indexer = SearchIndexer(("A", "title"), ("B", "description"))

    objects = PollQuerySet.as_manager()

    def __str__(self):
        return self.title


class Answer(models.Model):
    poll = models.ForeignKey(
        Poll, related_name="answers", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=180)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.description
