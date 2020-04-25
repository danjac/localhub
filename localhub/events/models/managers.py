# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.db.models.functions import Cast, ExtractWeekDay, Now, TruncWeek

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
        """

        If not repeating, just get the start date. Nothing more needed.

        We begin with base_date:

        1) for every day, return NOW().
        2) for weekdays:

        # get day of week (notice Cast to ensure int)
        # this is indexed from 1=Sunday through 7=Saturday.

        annotate(dow=Cast(ExtractWeekDay(F("starts")), IntegerField()))

        # get start of week: this will be MONDAY.

        annotate(sow=TruncWeek(Now()))

        # add dow MINUS 2 to sow (minus one b/c starting from Monday, minus 1 b/c of start index of 1)

        annotate(base_date=DayAdd(sow, F("dow") - 2))

        3) monthly: this assumes the 1st of every month:

        # get start of month:

        annotate(base_date=TruncMonth(Now()))

        4) annually: this assumes the same date as the start date.

        # we can just go with date.

        annotate(base_date=F("starts"))

        Now we have the base date, determine if it is in future. If in future, use that. If in past,
        we need to add the correct period.

        annotate(next_date=Case(
            When(Q(repeats__isnull=True), then=F("starts"))
            When(Q(base_date__gte=Now()), then=F("base_date"))
            When(Q(repeats="daily", then=DateAdd(F("base_date"), 1))),
            When(Q(repeats="weekly", then=DateAdd(F("base_date", 7)))),
            When(Q(repeats="monthly", then=MonthAdd(F("base_date", 1))))
            When(Q(repeats="yearly", then=YearAdd(F("base_date", 1)))),
            output_field=DateTimeField()
            )
        )
        """

        # Note: starts with MONDAY and is indexed from 1, so need to adjust by 2.
        return self.annotate(
            start_of_week=TruncWeek(Now()),
            day_of_week=Cast(ExtractWeekDay(models.F("starts")), models.IntegerField()),
            base_date=models.Case(
                models.When(models.Q(repeats__isnull=True), then=models.F("starts")),
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.WEEKLY),
                    then=DateAdd(
                        models.F("start_of_week"), models.F("day_of_week") - 2
                    ),
                ),
                output_field=models.DateTimeField(),
            ),
            next_date=models.Case(
                models.When(
                    models.Q(starts__gte=models.F("base_date")),
                    then=models.F("starts"),
                ),
                models.When(
                    repeats=self.model.RepeatChoices.WEEKLY,
                    then=DateAdd(models.F("base_date"), 7),
                ),
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
        Annotates "relevance" value based on start date and/or status.

        Relevance:
        1) if private/canceled: -1
        2) if event coming up: +1
        3) if event passed: 0

        Returns:
            QuerySet

        # TBD : replace starts with next_date
        """

        return self.annotate(
            relevance=models.Case(
                models.When(
                    models.Q(published__isnull=True) | models.Q(canceled__isnull=False),
                    then=models.Value(-1),
                ),
                models.When(starts__gte=Now(), then=models.Value(1)),
                default=0,
                output_field=models.IntegerField(),
            )
        )

    def with_timedelta(self):
        """
        Adds a DurationField with distance between now and the start time (future or past).

        Returns:
            QuerySet

        TBD: replace "starts" with "next_date"
        """
        return self.annotate(
            timedelta=models.Case(
                models.When(starts__gte=Now(), then=models.F("starts") - Now()),
                models.When(starts__lt=Now(), then=Now() - models.F("starts")),
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
