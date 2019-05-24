# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import geocoder

from typing import Optional, Tuple

from django.db import models
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField

from model_utils import FieldTracker

from communikit.activities.models import Activity
from communikit.markdown.fields import MarkdownField


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

    location_tracker = FieldTracker(LOCATION_FIELDS)

    def __str__(self) -> str:
        return self.title or self.location

    def search_index_components(self):
        return {"A": self.title, "B": self.location, "C": self.description}

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
        return ", ".join(
            [
                smart_text(value)
                for value in [
                    getattr(self, field) for field in self.LOCATION_FIELDS
                ]
                if value
            ]
        )
