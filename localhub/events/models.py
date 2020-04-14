# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import geopy
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from icalendar import Calendar
from icalendar import Event as CalendarEvent
from timezone_field import TimeZoneField

from localhub.activities.models import Activity, ActivityQuerySet
from localhub.db.search import SearchIndexer
from localhub.db.tracker import Tracker
from localhub.db.utils import boolean_value
from localhub.utils.http import get_domain

geolocator = geopy.Nominatim(user_agent=settings.LOCALHUB_GEOLOCATOR_USER_AGENT)


class EventQuerySet(ActivityQuerySet):
    def with_num_attendees(self):
        return self.annotate(num_attendees=models.Count("attendees"))

    def is_attending(self, user):
        return self.annotate(
            is_attending=boolean_value(False)
            if user.is_anonymous
            else models.Exists(self.model.objects.filter(attendees=user))
        )

    def with_common_annotations(self, user, community):
        return (
            super()
            .with_common_annotations(user, community)
            .with_num_attendees()
            .is_attending(user)
        )


class Event(Activity):

    # not exhaustive!

    ADDRESS_FORMATS = (
        (
            ("GB", "IN", "PK", "ZA", "JP"),
            "{street_address}, {locality}, {region}, {postcode}, {country}",
        ),
        (
            ("US", "AU", "NZ"),
            "{street_address} {locality}, {postcode}, {region}, {country}",
        ),
        (("RU",), "{street_address} {locality} {postcode}, {region}, {country}"),
    )

    # default for Europe, S. America, China, S. Korea
    DEFAULT_ADDRESS_FORMAT = (
        "{street_address}, {postcode} {locality}, {region}, {country}"
    )

    LOCATION_FIELDS = (
        "street_address",
        "locality",
        "postal_code",
        "region",
        "country",
    )

    RESHARED_FIELDS = (
        Activity.RESHARED_FIELDS
        + LOCATION_FIELDS
        + (
            "url",
            "starts",
            "ends",
            "timezone",
            "venue",
            "ticket_price",
            "ticket_vendor",
            "latitude",
            "longitude",
        )
    )

    url = models.URLField(verbose_name=_("Link"), max_length=500, null=True, blank=True)

    starts = models.DateTimeField(verbose_name=_("Starts on (UTC)"))
    ends = models.DateTimeField(null=True, blank=True)
    timezone = TimeZoneField(default=settings.TIME_ZONE)

    venue = models.CharField(max_length=200, blank=True)

    ticket_price = models.CharField(max_length=200, blank=True)
    ticket_vendor = models.TextField(
        verbose_name=_("Tickets available from"), blank=True
    )

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

    location_tracker = Tracker(LOCATION_FIELDS)

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "indexable_location"), ("C", "description")
    )

    objects = EventQuerySet.as_manager()

    def __str__(self):
        return self.title or self.location

    def clean(self):
        if self.ends and self.ends < self.starts:
            raise ValidationError(_("End date cannot be before start date"))

    def get_domain(self):
        return get_domain(self.url) or ""

    def get_starts_with_tz(self):
        """Returns timezone-adjusted start time.

        Returns:
            datetime
        """
        return self.starts.astimezone(self.timezone)

    def get_ends_with_tz(self):
        """Returns timezone-adjusted end time.

        Returns:
            datetime or None: returns None if ends is None.
        """
        return self.ends.astimezone(self.timezone) if self.ends else None

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
        return all((self.latitude, self.longitude))

    def get_address_format(self):
        if not self.country:
            return self.DEFAULT_ADDRESS_FORMAT

        for codes, address_format in self.ADDRESS_FORMATS:
            if self.country.code in codes:
                return address_format

        return self.DEFAULT_ADDRESS_FORMAT

    def has_started(self):
        return self.starts < timezone.now()

    def to_ical(self):
        event = CalendarEvent()

        starts = self.get_starts_with_tz()
        ends = self.get_ends_with_tz()

        event.add("dtstart", starts)
        event.add("dtstamp", starts)
        if ends:
            event.add("dtend", ends)
        event.add("summary", self.title)

        location = self.get_full_location()
        if location:
            event.add("location", location)

        if self.description:
            event.add("description", self.description)

        calendar = Calendar()
        calendar.add_component(event)
        return calendar.to_ical()
