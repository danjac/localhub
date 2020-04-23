# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from localhub.activities.models import Activity, ActivityQuerySet
from localhub.db.search.indexer import SearchIndexer
from localhub.notifications.decorators import dispatch


class PollQuerySet(ActivityQuerySet):
    def with_answers(self):
        return self.prefetch_related(
            models.Prefetch(
                "answers",
                queryset=Answer.objects.annotate(
                    num_votes=models.Count("voters", distinct=True)
                ).order_by("id"),
            )
        )

    def for_activity_stream(self, user, community):
        return super().for_activity_stream(user, community).with_answers()


class Poll(Activity):

    allow_voting = models.BooleanField(default=True)

    search_indexer = SearchIndexer(("A", "title"), ("B", "indexable_description"))

    objects = PollQuerySet.as_manager()

    def __str__(self):
        return self.title or _("Poll")

    @cached_property
    def total_num_votes(self):
        """
        Returns number of votes. Use in conjunction with with_answers()
        method in queryset!
        """
        return sum([a.num_votes for a in self.answers.all()])

    @dispatch
    def notify_on_vote(self, voter):
        """
        Sends a notification when someone has voted. Ignore if you
        vote on your own poll.
        """
        if voter != self.owner:
            return self.make_notification(self.owner, "vote", voter)
        return None


class Answer(models.Model):
    poll = models.ForeignKey(Poll, related_name="answers", on_delete=models.CASCADE)
    description = models.CharField(max_length=180)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.description
