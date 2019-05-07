from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

from communikit.communities.models import Community


class Invite(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    email = models.EmailField()
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
