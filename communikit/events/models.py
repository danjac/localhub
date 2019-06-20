# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import geocoder

from typing import Dict, Optional, List, Tuple

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_text
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from model_utils import FieldTracker

from communikit.activities.models import Activity
from communikit.activities.utils import get_domain
from communikit.core.markdown.fields import MarkdownField
from communikit.notifications.models import Notification


class Event(Activity):
    LOCATION_FIELDS = (
        "street_address",
        "locality",
        "postal_code",
        "region",
        "country",
    )

    title = models.CharField(max_length=200)
    url = models.URLField(verbose_name=_("Link"), null=True, blank=True)
    description = MarkdownField(blank=True)

    starts = models.DateTimeField()
    ends = models.DateTimeField(null=True, blank=True)

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

    notifications = GenericRelation(Notification, related_query_name="event")

    description_tracker = FieldTracker(["description"])
    location_tracker = FieldTracker(LOCATION_FIELDS)

    list_url_name = "events:list"
    detail_url_name = "events:detail"

    def __str__(self) -> str:
        return self.title or self.location

    def clean(self):
        if self.ends and self.ends < self.starts:
            raise ValidationError(_("End date cannot be before start date"))

    def get_domain(self) -> Optional[str]:
        return get_domain(self.url)

    def search_index_components(self) -> Dict[str, str]:
        return {
            "A": self.title,
            "B": self.full_location,
            "C": self.description,
        }

    def update_coordinates(self) -> Tuple[Optional[float], Optional[float]]:
        if self.location:
            result = geocoder.osm(self.location)
            self.latitude, self.longitude = result.lat, result.lng
        else:
            self.latitude, self.longitude = None, None
        self.__class__._default_manager.filter(pk=self.id).update(
            latitude=self.latitude, longitude=self.longitude
        )
        return self.latitude, self.longitude

    @property
    def location(self) -> str:
        rv: List[str] = [
            smart_text(value)
            for value in [
                getattr(self, field) for field in self.LOCATION_FIELDS[:-1]
            ]
            if value
        ]

        if self.country:
            rv.append(smart_text(self.country.name))
        return ", ".join(rv)

    @property
    def full_location(self) -> str:
        """
        Includes venue if available
        """
        return ", ".join(
            [
                smart_text(value)
                for value in [self.venue, self.location]
                if value
            ]
        )

    def notify(self, created: bool) -> List[Notification]:
        notifications: List[Notification] = []
        # notify anyone @mentioned in the description
        if self.description and (
            created or self.description_tracker.changed()
        ):
            notifications += [
                Notification(
                    content_object=self,
                    actor=self.owner,
                    community=self.community,
                    recipient=recipient,
                    verb="mentioned",
                )
                for recipient in self.community.members.matches_usernames(
                    self.description.extract_mentions()
                ).exclude(pk=self.owner_id)
            ]

        # notify all community moderators
        verb = "created" if created else "updated"
        notifications += [
            Notification(
                content_object=self,
                actor=self.owner,
                community=self.community,
                recipient=recipient,
                verb=verb,
            )
            for recipient in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        Notification.objects.bulk_create(notifications)
        return notifications
