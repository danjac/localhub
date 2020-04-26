# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.db import models
from django.db.models.functions import (
    Cast,
    ExtractWeekDay,
    Now,
    TruncDay,
    TruncMonth,
    TruncWeek,
)
from django.utils import timezone

import pytz

from localhub.activities.models.managers import ActivityManager, ActivityQuerySet
from localhub.db.functions import DateAdd, MonthAdd, YearAdd
from localhub.db.utils import boolean_value


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
                models.When(next_date__gte=Now(), then=models.F("next_date") - Now()),
                models.When(next_date__lt=Now(), then=Now() - models.F("next_date")),
                output_field=models.DurationField(),
            )
        )

    def for_date(self, day, month, year):
        """For convenience: given a day/month/year, return
        events for this date.
        """
        return self.for_dates(
            datetime.datetime(day=day, month=month, year=year, tzinfo=pytz.UTC)
        )

    def for_month(self, month, year):
        """For convenience: given a month/year, return events
        within the 1st and last of month (i.e. 11:59:59 of last month)
        """

        date_from = datetime.datetime(day=1, month=month, year=year, tzinfo=pytz.UTC)

        (_, last) = calendar.monthrange(year, month)

        date_to = datetime.datetime(
            day=last,
            month=month,
            year=year,
            hour=23,
            minute=59,
            second=59,
            tzinfo=pytz.UTC,
        )

        return self.for_dates(date_from, date_to)

    def for_dates(self, date_from, date_to=None):
        """Returns:

        1) non-repeating dates with date range falling within these dates OR
        2) repeating dates with start date > the date from date
        """

        non_repeats_q = models.Q(repeats__isnull=True) | models.Q(
            repeats_until__lte=timezone.now()
        )

        repeats_q = models.Q(
            models.Q(
                models.Q(repeats_until__isnull=True)
                | models.Q(repeats_until__gte=date_from)
            ),
            repeats__isnull=False,
        )

        if date_to is None:
            # fetch all those for a specific date
            non_repeats_q = non_repeats_q & models.Q(
                starts__day=date_from.day,
                starts__month=date_from.month,
                starts__year=date_from.year,
            )
            # any that have already started BEFORE the date_from
            # and so will have started repeating, plus any
            # that start specifically today
            repeats_q = repeats_q & models.Q(
                models.Q(starts__lte=date_from)
                | models.Q(
                    starts__day=date_from.day,
                    starts__month=date_from.month,
                    starts__year=date_from.year,
                )
            )
        else:
            non_repeats_q = non_repeats_q & models.Q(starts__range=(date_from, date_to))
            # any that have already started BEFORE the date_from
            # OR will start with the range
            repeats_q = repeats_q & models.Q(
                models.Q(starts__range=(date_from, date_to))
                | models.Q(starts__lte=date_from)
            )

        return self.filter(non_repeats_q | repeats_q)

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
