from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel


class Like(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
