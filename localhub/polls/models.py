# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from localhub.activities.models import Activity, ActivityQuerySet
from localhub.db.search import SearchIndexer


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
    RESHARED_FIELDS = ("title", "description")

    title = models.CharField(max_length=300)

    search_indexer = SearchIndexer(("A", "title"), ("B", "description"))

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


class Answer(models.Model):
    poll = models.ForeignKey(Poll, related_name="answers", on_delete=models.CASCADE)
    description = models.CharField(max_length=180)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.description
