# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import apps
from django.db import models

from localhub.apps.activities.models.managers import ActivityManager, ActivityQuerySet


class PollQuerySet(ActivityQuerySet):
    def with_answers(self):
        return self.prefetch_related(
            models.Prefetch(
                "answers",
                queryset=apps.get_model("polls.Answer")
                .objects.annotate(num_votes=models.Count("voters", distinct=True))
                .order_by("id"),
            )
        )

    def for_activity_stream(self, user, community):
        return super().for_activity_stream(user, community).with_answers()


class PollManager(ActivityManager.from_queryset(PollQuerySet)):
    ...
