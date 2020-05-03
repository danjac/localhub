# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
from django.utils.encoding import smart_text
from django.utils.translation import gettext_lazy as _

import pytz
from django_countries.fields import CountryField
from icalendar import Calendar
from icalendar import Event as CalendarEvent
from timezone_field import TimeZoneField

from bfg.apps.activities.models import Activity, ActivityManager, ActivityQuerySet
from bfg.apps.notifications.decorators import notify
from bfg.db.functions import DateAdd, MonthAdd, YearAdd
from bfg.db.search.indexer import SearchIndexer
from bfg.db.utils import boolean_value
from bfg.utils.http import get_domain


class EventQuerySet(ActivityQuerySet):
    def with_next_date(self):
        """Returns the next date this event occurs.

        For one-time events, this will just be the "starts" value. For repeating
        events we need to calculate the next date based on the repeating criteria
        from the time the repetition begins, i.e. at or after the start date.

        Returns:
            QuerySet
        """
        now = timezone.now()
        return self.annotate(
            start_of_day=TruncDay(Now()),
            start_of_week=TruncWeek(Now()),
            day_of_week=Cast(ExtractWeekDay(models.F("starts")), models.IntegerField()),
            # base date : we first calculate a base date, and add the correct interval
            # to this date to get the next date.
            base_date=models.Case(
                # starts today: just use today
                models.When(
                    models.Q(
                        starts__day=now.day,
                        starts__month=now.month,
                        starts__year=now.year,
                    ),
                    then=Now(),
                ),
                # repeats daily: from this morning
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.DAILY),
                    then=models.F("start_of_day"),
                ),
                # repeats weekly: from first day of week (Sunday)
                # Note: starts with MONDAY and is indexed from 1, so need to adjust by -2.
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.WEEKLY),
                    then=DateAdd(
                        models.F("start_of_week"), models.F("day_of_week") - 2
                    ),
                ),
                # repeats monthly: from 1st of this month
                models.When(
                    models.Q(repeats=self.model.RepeatChoices.MONTHLY),
                    then=TruncMonth(Now()),
                ),
                default=models.F("starts"),
                output_field=models.DateTimeField(),
            ),
            next_date=models.Case(
                # the start date.
                models.When(
                    models.Q(starts__gte=models.F("base_date"))
                    & models.Q(starts__gte=Now()),
                    then=models.F("starts"),
                ),
                # daily: base date + 1 day
                models.When(
                    repeats=self.model.RepeatChoices.DAILY,
                    then=DateAdd(models.F("base_date"), 1),
                ),
                # weekly: base date + 7 days
                models.When(
                    repeats=self.model.RepeatChoices.WEEKLY,
                    then=DateAdd(models.F("base_date"), 7),
                ),
                # monthly: base date + 1 month (i.e. 1st of next month)
                models.When(
                    repeats=self.model.RepeatChoices.MONTHLY,
                    then=MonthAdd(models.F("base_date"), 1),
                ),
                # yearly: base date + 1 year
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
        2) if event coming up OR same day as today: +1
        3) if event passed: 0

        Returns:
            QuerySet
        """
        now = timezone.now()

        return self.annotate(
            relevance=models.Case(
                models.When(
                    models.Q(published__isnull=True) | models.Q(canceled__isnull=False),
                    then=models.Value(-1),
                ),
                models.When(
                    models.Q(
                        models.Q(next_date__gte=now)
                        | models.Q(
                            next_date__day=now.day,
                            next_date__month=now.month,
                            next_date__year=now.year,
                        )
                    ),
                    then=models.Value(1),
                ),
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

        Args:
            day (int): day of month i.e. 1-31.
            month (int): calendar month i.e. 1-12
            year (int): calendar year

        Returns:
            QuerySet

        Raises:
            Event.InvalidDate: if day/month/year combo is not a valid
                calendar date.
        """
        try:
            dt = datetime.datetime(day=day, month=month, year=year, tzinfo=pytz.UTC)
        except ValueError:
            raise self.model.InvalidDate()
        return self.for_dates(dt)

    def for_month(self, month, year):
        """For convenience: given a month/year, return events
        within the 1st and last of month (i.e. 11:59:59 of last month)

        Args:
            month (int): calendar month i.e. 1-12
            year (int): calendar year

        Returns:
            QuerySet

        Raises:
            Event.InvalidDate: if month/year combo is not a valid
                calendar date.
        """
        try:
            date_from = datetime.datetime(
                day=1, month=month, year=year, tzinfo=pytz.UTC
            )

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
        except ValueError:
            raise self.model.InvalidDate()

        return self.for_dates(date_from, date_to)

    def for_dates(self, date_from, date_to=None):
        """Returns any events which either start within
        these dates or (if repeating) are valid within these
        dates.

        To check specific dates within these ranges to see
        if an event actually occurs on that date, use this
        filter with Event.matches_date().

        Args:
            date_from (date or datetime)
            date_to (date or datetime, optional): if this is provided
                will check range of dates
        Returns:
            QuerySet
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


class Event(Activity):

    # not exhaustive!

    ADDRESS_FORMATS = [
        (
            ("GB", "IN", "PK", "ZA", "JP"),
            "{street_address}, {locality}, {region}, {postcode}, {country}",
        ),
        (
            ("US", "AU", "NZ"),
            "{street_address} {locality}, {postcode}, {region}, {country}",
        ),
        (("RU",), "{street_address} {locality} {postcode}, {region}, {country}",),
    ]

    # default for Europe, S. America, China, S. Korea
    DEFAULT_ADDRESS_FORMAT = (
        "{street_address}, {postcode} {locality}, {region}, {country}"
    )

    LOCATION_FIELDS = [
        "street_address",
        "locality",
        "postal_code",
        "region",
        "country",
    ]

    RESHARED_FIELDS = (
        Activity.RESHARED_FIELDS
        + LOCATION_FIELDS
        + ["url", "starts", "ends", "timezone", "venue", "latitude", "longitude",]
    )

    class InvalidDate(ValueError):
        """Used with date queries"""

        ...

    class RepeatChoices(models.TextChoices):
        DAILY = "day", _("Same time every day")
        WEEKLY = "week", _("Same day of the week at the same time")
        MONTHLY = (
            "month",
            _("First day of the month at the same time"),
        )
        YEARLY = "year", _("Same date and time every year")

    url = models.URLField(verbose_name=_("Link"), max_length=500, null=True, blank=True)

    starts = models.DateTimeField(verbose_name=_("Starts on (UTC)"))
    # Note: "ends" must be same day if repeating
    ends = models.DateTimeField(null=True, blank=True)

    repeats = models.CharField(
        max_length=20, choices=RepeatChoices.choices, null=True, blank=True
    )
    repeats_until = models.DateTimeField(null=True, blank=True)

    timezone = TimeZoneField(default=settings.TIME_ZONE)

    canceled = models.DateTimeField(null=True, blank=True)

    venue = models.CharField(max_length=200, blank=True)

    street_address = models.CharField(max_length=200, blank=True)
    locality = models.CharField(
        verbose_name=_("City or town"), max_length=200, blank=True
    )
    postal_code = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=200, blank=True)
    country = CountryField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="attending_events"
    )

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "indexable_location"), ("C", "indexable_description"),
    )

    objects = EventManager()

    class Meta(Activity.Meta):
        indexes = Activity.Meta.indexes + [
            models.Index(fields=["starts"], name="event_starts_idx")
        ]

    def __str__(self):
        return self.title or self.location

    def clean(self):
        if self.ends and self.ends < self.starts:
            raise ValidationError(_("End date cannot be before start date"))

        if self.ends and self.ends.date() != self.starts.date() and self.repeats:
            raise ValidationError(_("End date must be same as start date if repeating"))

        if self.repeats_until and not self.repeats:
            raise ValidationError(
                _("Repeat until date cannot be set if not a repeating event")
            )

        if self.repeats_until and self.repeats_until < self.starts:
            raise ValidationError(_("Repeat until date cannot be before start date"))

    def get_domain(self):
        return get_domain(self.url) or ""

    def get_next_starts_with_tz(self):
        """Returns timezone-adjusted start time.

        Returns:
            datetime
        """
        return self.get_next_start_date().astimezone(self.timezone)

    def get_next_ends_with_tz(self):
        """Returns timezone-adjusted end time.

        Returns:
            datetime or None: returns None if ends is None.
        """
        if ends := self.get_next_end_date():
            return ends.astimezone(self.timezone)
        return None

    def get_location(self):
        """Returns a concatenated string of location fields.

        Will try to guess the correct format based on country.

        If any missing fields, will try to tidy up the string to remove
        any trailing commas and spaces.

        Returns:
            str
        """
        location = (
            self.get_address_format()
            .format(
                street_address=self.street_address,
                locality=self.locality,
                region=self.region,
                postcode=self.postal_code,
                country=self.country.name if self.country else "",
            )
            .replace("  ", " ")
            .replace(", ,", ", ")
            .strip()
        )
        # if location is just commas and spaces, return an empty string
        if location.replace(",", "").strip() == "":
            return ""

        if location.endswith(","):
            location = location[:-1]
        return smart_text(location)

    def get_full_location(self):
        """Includes venue if available along with location.

        Returns:
            str
        """
        return ", ".join(
            [smart_text(value) for value in [self.venue, self.get_location()] if value]
        )

    def get_geocoder_location(self):
        """Return a standard location for OSM lookup:
        - street address
        - locality
        - postal code
        - country name

        Returns:
            dict or None: returns None if any required fields are missing.
        """

        fields = {
            "street": self.street_address,
            "city": self.locality,
            "postalcode": self.postal_code,
            "country": self.country.name if self.country else None,
        }
        if not all(fields.values()):
            return None

        return fields

    @property
    def indexable_location(self):
        """Property required for search indexer. Just returns full location.
        """
        return self.get_full_location()

    def has_map(self):
        return all((self.latitude, self.longitude)) and not self.canceled

    def get_address_format(self):
        if not self.country:
            return self.DEFAULT_ADDRESS_FORMAT

        for codes, address_format in self.ADDRESS_FORMATS:
            if self.country.code in codes:
                return address_format

        return self.DEFAULT_ADDRESS_FORMAT

    def has_started(self):
        """If start date in past, unless still repeating.

        Returns:
            bool
        """
        if self.is_repeating():
            return False
        return self.starts < timezone.now()

    def has_ended(self):
        """If end date in past, unless still repeating.

        If end date is None, assumes the end of the same
        day as the start date.

        Returns:
            bool
        """
        if self.is_repeating():
            return False
        if self.ends is None:
            return self.starts.replace(hour=23, minute=59, second=59) < timezone.now()
        return self.ends < timezone.now()

    def get_next_start_date(self):
        """Returns next_date if repeating, otherwise starts.

        Note that this must be used with the with_next_date() QuerySet
        method.
        """
        if not self.is_repeating():
            return self.starts

        if not hasattr(self, "next_date"):
            raise AttributeError(
                "next_date not present: must be used with EventQuerySet.with_next_date()"
            )
        # ensure date/times preserved
        return self.next_date.replace(hour=self.starts.hour, minute=self.starts.minute)

    def get_next_end_date(self):

        """Returns the next_date plus ends time (must be same date as the start date)

        Note that this must be used with the with_next_date() QuerySet
        method.
        """

        if not self.ends or not self.is_repeating():
            return self.ends

        if not hasattr(self, "next_date"):
            raise AttributeError(
                "next_date not present: must be used with EventQuerySet.with_next_date()"
            )

        return self.ends.replace(
            day=self.next_date.day,
            month=self.next_date.month,
            year=self.next_date.year,
        )

    def is_repeating(self):
        """If has repeat option, and repeats_until is NULL or
        in future.

        Returns:
            bool
        """
        if not self.repeats:
            return False
        if self.repeats_until is None:
            return True
        return self.repeats_until > timezone.now()

    def repeats_daily(self):
        return self.repeats == self.RepeatChoices.DAILY

    def repeats_weekly(self):
        return self.repeats == self.RepeatChoices.WEEKLY

    def repeats_monthly(self):
        return self.repeats == self.RepeatChoices.MONTHLY

    def repeats_yearly(self):
        return self.repeats == self.RepeatChoices.YEARLY

    def is_attendable(self):
        """If event can be attended:
            - start date in future
            - not private
            - not canceled or deleted
        Returns:
            bool
        """
        return all(
            (
                self.published,
                not (self.deleted),
                not (self.canceled),
                not (self.has_started()),
            )
        )

    def matches_date(self, dt):
        """Checks if event has a date matching this date. Useful e.g.
        for scrolling through a list of dates.

        Args:
            dt (datetime)

        Returns:
            bool: if event occurs on this date (single or repeating)
        """
        exact_match = (
            self.starts.day == dt.day
            and self.starts.month == dt.month
            and self.starts.year == dt.year
        )

        # if non-repeating then must always be an exact match.
        if not self.is_repeating():
            return exact_match

        # matches IF:
        # 1) has already started repeating (dt > starts)
        # 2) now or dt < repeats_until
        # 3) dt matches the appropriate repeats criteria.

        if not exact_match and self.starts > dt:
            return False

        if self.repeats_until and (
            self.repeats_until < dt or self.repeats_until < timezone.now()
        ):
            return False

        if self.repeats == self.RepeatChoices.DAILY:
            return True

        if self.repeats == self.RepeatChoices.WEEKLY:
            return dt.weekday() == self.starts.weekday()

        if self.repeats == self.RepeatChoices.MONTHLY:
            return dt.day == 1

        if self.repeats == self.RepeatChoices.YEARLY:
            return dt.day == self.starts.day and dt.month == self.starts.month

        return False

    @notify
    def notify_on_attend(self, attendee):
        """Notifies owner (if not themselves the attendee) of attendance.
        Args:
            actor (User)

        Returns:
            list (List[Notification])
        """
        if attendee == self.owner:
            return None
        return self.make_notification(
            recipient=self.owner, actor=attendee, verb="attend"
        )

    @notify
    def notify_on_cancel(self, actor):
        """Notify all attendees of cancellation. Also notify the event
        owner if the actor is not the owner.

        Args:
            actor (User)

        Returns:
            list (List[Notification])
        """
        recipients = self.attendees.exclude(pk=actor.pk)
        if actor == self.owner:
            recipients = recipients.exclude(pk=self.owner.pk)
        else:
            recipients = recipients | get_user_model().objects.filter(pk=self.owner.pk)

        recipients = recipients.filter(
            membership__active=True, membership__community=self.community
        )

        return [
            self.make_notification(recipient=recipient, actor=actor, verb="cancel")
            for recipient in recipients
        ]

    def to_ical(self):
        """Returns iCalendar event object.

        Returns:
            Calendar
        """
        event = CalendarEvent()

        starts = self.get_next_starts_with_tz()

        event.add("dtstart", starts)
        event.add("dtstamp", starts)

        if ends := self.get_next_ends_with_tz():
            event.add("dtend", ends)

        event.add("summary", self.title)

        if location := self.get_full_location():
            event.add("location", location)

        if self.description:
            event.add("description", self.description.plaintext().splitlines())

        calendar = Calendar()
        calendar.add_component(event)
        return calendar.to_ical()
