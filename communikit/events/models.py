from django.db import models
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField

from model_utils import FieldTracker

from communikit.content.models import Post


class Event(Post):

    LOCATION_FIELDS = (
        "street_address",
        "locality",
        "postal_code",
        "region",
        "country",
    )

    starts = models.DateTimeField()
    ends = models.DateTimeField(null=True, blank=True)

    street_address = models.CharField(max_length=200, blank=True)
    locality = models.CharField(
        verbose_name=_("City or town"), max_length=200, blank=True
    )
    postal_code = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=200, blank=True)
    country = CountryField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    tracker = FieldTracker(LOCATION_FIELDS)

    def __str__(self) -> str:
        return self.title or self.location

    @property
    def location(self):
        return ", ".join(
            [
                value
                for value in [
                    smart_text(getattr(self, field))
                    for field in self.LOCATION_FIELDS
                ]
                if value
            ]
        )
