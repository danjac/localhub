import geocoder

from typing import Optional, Tuple

from django.db import models

from model_utils import FieldTracker

from communikit.content.models import Post


class Event(Post):

    starts = models.DateTimeField()
    ends = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=300, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    tracker = FieldTracker(["location"])

    def __str__(self) -> str:
        return self.title or self.location
