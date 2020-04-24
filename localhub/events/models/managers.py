# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils import timezone

from localhub.activities.models.managers import ActivityManager, ActivityQuerySet
from localhub.db.utils import boolean_value

# TBD: these will live in a utils module


def next_day(dt):
    ...


def next_weekday(dt):
    ...


def next_month_date(dt):
    ...


def next_annual_date(dt):
    ...


class EventQuerySet(ActivityQuerySet):
    def with_next_date(self):
        """Annotates "next_date" accordingly:

        1) if repeating, next day/matching weekday/day of month/annual date
        2) if not repeating, start date.
        """
        now = timezone.now()

        return self.annotate(
            next_day=models.Case(
                models.When(
                    models.Q(
                        repeats_until__gt=now, repeats=self.model.RepeatsChoices.DAILY,
                    ),
                    then=models.Value(next_day(models.F("starts"))),
                ),
                models.When(
                    models.Q(
                        repeats_until__gt=now, repeats=self.model.RepeatsChoices.WEEKLY,
                    ),
                    then=models.Value(next_weekday(models.F("starts"))),
                ),
                models.When(
                    models.Q(
                        repeats_until__gt=now,
                        repeats=self.model.RepeatsChoices.MONTHLY,
                    ),
                    then=models.Value(next_month_date(models.F("starts"))),
                ),
                models.When(
                    models.Q(
                        repeats_until__gt=now, repeats=self.model.RepeatsChoices.YEARLY,
                    ),
                    then=models.Value(next_annual_date(models.F("starts"))),
                ),
                default=models.F("starts"),
                output_value=models.DateTime(),
            )
        )

    def is_attending(self, user):
        """Annotates "is_attending" if user is attending the event.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        return self.annotate(
            is_attending=boolean_value(False)
            if user.is_anonymous
            else models.Exists(
                self.model.objects.filter(attendees=user, pk=models.OuterRef("pk"))
            )
        )

    def with_num_attendees(self):
        """Annotates "num_attendees" to each event.

        Returns:
            QuerySet
        """
        return self.annotate(num_attendees=models.Count("attendees"))

    def with_relevance(self):
        """
        Annotates "relevance" value based on start date and/or status.

        Relevance:
        1) if private/canceled: -1
        2) if event coming up: +1
        3) if event passed: 0

        Returns:
            QuerySet
        """

        return self.annotate(
            relevance=models.Case(
                models.When(
                    models.Q(published__isnull=True) | models.Q(canceled__isnull=False),
                    then=models.Value(-1),
                ),
                models.When(starts__gte=timezone.now(), then=models.Value(1)),
                default=0,
                output_field=models.IntegerField(),
            )
        )

    def with_timedelta(self):
        """
        Adds a DurationField with distance between now and the start time (future or past).

        Returns:
            QuerySet
        """
        now = timezone.now()
        return self.annotate(
            timedelta=models.Case(
                models.When(starts__gte=now, then=models.F("starts") - now),
                models.When(starts__lt=now, then=now - models.F("starts")),
                output_field=models.DurationField(),
            )
        )

    def with_common_annotations(self, user, community):
        return (
            super()
            .with_common_annotations(user, community)
            .with_num_attendees()
            .is_attending(user)
        )


class EventManager(ActivityManager.from_queryset(EventQuerySet)):
    ...
