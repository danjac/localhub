from django.db import models

from communikit.content.models import Post


class Event(Post):

    starts = models.DateTimeField()
    ends = models.DateTimeField(null=True, blank=True)

    location = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self) -> str:
        return self.title or self.location
