# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.db.models.functions import (
    Cast,
    ExtractWeekDay,
    Now,
    TruncDay,
    TruncMonth,
    TruncWeek,
)

from localhub.activities.models.managers import ActivityManager, ActivityQuerySet
from localhub.db.utils import boolean_value

# this should go under localhub.db.functions


class IntervalAdd(models.Func):
    period = None
    arg_joiner = " + CAST("
    output_field = models.DateTimeField()

    @property
    def template(self):
        return "%(expressions)s || '" + self.period + "' AS INTERVAL)"


class DateAdd(IntervalAdd):
    period = "days"


class MonthAdd(IntervalAdd):
    period = "months"


class YearAdd(IntervalAdd):
    period = "years"


class EventQuerySet(ActivityQuerySet):
    def with_next_date(self):
        return self.annotate(
            start_of_day=TruncDay(Now()),
            start_of_week=TruncWeek(Now()),
            # Note: starts with MONDAY and is indexed from 1, so need to adjust by -2.
            day_of_week=Cast(ExtractWeekDay(models.F("starts")), models.IntegerField()),
            base_date=models.Case(
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.DAILY),
                    then=models.F("start_of_day"),
                ),
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.WEEKLY),
                    then=DateAdd(
                        models.F("start_of_week"), models.F("day_of_week") - 2
                    ),
                ),
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.MONTHLY),
                    then=TruncMonth(Now()),
                ),
                default=models.F("starts"),
                output_field=models.DateTimeField(),
            ),
            next_date=models.Case(
                models.When(
                    models.Q(starts__gte=models.F("base_date"))
                    & models.Q(starts__gte=Now()),
                    then=models.F("starts"),
                ),
                models.When(
                    repeats=self.model.RepeatChoices.DAILY,
                    then=DateAdd(models.F("base_date"), 1),
                ),
                models.When(
                    repeats=self.model.RepeatChoices.WEEKLY,
                    then=DateAdd(models.F("base_date"), 7),
                ),
                models.When(
                    repeats=self.model.RepeatChoices.MONTHLY,
                    then=MonthAdd(models.F("base_date"), 1),
                ),
                models.When(
                    repeats=self.model.RepeatChoices.YEARLY,
                    then=YearAdd(models.F("base_date"), 1),
                ),
                default=models.F("starts"),
                output_field=models.DateTimeField(),
            ),
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
        Annotates "relevance" value based on next date and/or status.

        Use with with_next_date() !

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
                models.When(next_date__gte=Now(), then=models.Value(1)),
                default=0,
                output_field=models.IntegerField(),
            )
        )

    def with_timedelta(self):
        """
        Adds a DurationField with distance between now and the start time (future or past).

        Use with with_next_date() !

        Returns:
            QuerySet
        """
        return self.annotate(
            timedelta=models.Case(
                models.When(starts__gte=Now(), then=models.F("next_date") - Now()),
                models.When(starts__lt=Now(), then=Now() - models.F("next_date")),
                output_field=models.DurationField(),
            )
        )

    def with_common_annotations(self, user, community):
        return (
            super()
            .with_common_annotations(user, community)
            .with_num_attendees()
            .with_next_date()
            .is_attending(user)
        )


class EventManager(ActivityManager.from_queryset(EventQuerySet)):
    ...
