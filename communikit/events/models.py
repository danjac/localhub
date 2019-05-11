from django.db import models

from communikit.content.models import Post


class Event(Post):

    starts = models.DateTimeField()
    ends = models.DateTimeField(null=True, blank=True)
    location = models.TextField(blank=True)
