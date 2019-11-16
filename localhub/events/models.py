# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import geocoder
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_text
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from icalendar import Calendar
from icalendar import Event as CalendarEvent
from timezone_field import TimeZoneField

from localhub.activities.models import Activity
from localhub.activities.utils import get_domain
from localhub.comments.models import Comment
from localhub.core.db.search import SearchIndexer
from localhub.core.db.tracker import Tracker
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification


class Event(Activity):

    LOCATION_FIELDS = (
        "street_address",
        "locality",
        "postal_code",
        "region",
        "country",
    )

    RESHARED_FIELDS = LOCATION_FIELDS + (
        "title",
        "description",
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

    title = models.CharField(max_length=200)
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

    comments = GenericRelation(Comment, related_query_name="event")
    flags = GenericRelation(Flag, related_query_name="event")
    likes = GenericRelation(Like, related_query_name="event")
    notifications = GenericRelation(Notification, related_query_name="event")

    location_tracker = Tracker(LOCATION_FIELDS)

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "full_location"), ("C", "description")
    )

    def __str__(self):
        return self.title or self.location

    def clean(self):
        if self.ends and self.ends < self.starts:
            raise ValidationError(_("End date cannot be before start date"))

    def get_domain(self):
        return get_domain(self.url)

    def get_starts_with_tz(self):
        return self.starts.astimezone(self.timezone)

    def get_ends_with_tz(self):
        return self.ends.astimezone(self.timezone) if self.ends else None

    def update_coordinates(self):
        """
        Fetches the lat/lng coordinates from Open Street Map API.
        """
        if self.location:
            result = geocoder.osm(self.location)
            self.latitude, self.longitude = result.lat, result.lng
        else:
            self.latitude, self.longitude = None, None
        self.save(update_fields=["latitude", "longitude"])
        return self.latitude, self.longitude

    @property
    def location(self):
        """
        Returns a concatenated string of location fields.
        """
        rv = [
            smart_text(value)
            for value in [getattr(self, field) for field in self.LOCATION_FIELDS[:-1]]
            if value
        ]

        if self.country:
            rv.append(smart_text(self.country.name))
        return ", ".join(rv)

    @property
    def full_location(self):
        """
        Includes venue if available
        """
        return ", ".join(
            [smart_text(value) for value in [self.venue, self.location] if value]
        )

    def to_ical(self):
        event = CalendarEvent()

        starts = self.get_starts_with_tz()
        ends = self.get_ends_with_tz()

        event.add("dtstart", starts)
        event.add("dtstamp", starts)
        if ends:
            event.add("dtend", ends)
        event.add("summary", self.title)

        location = self.full_location
        if location:
            event.add("location", location)

        if self.description:
            event.add("description", self.description)

        calendar = Calendar()
        calendar.add_component(event)
        return calendar.to_ical()
