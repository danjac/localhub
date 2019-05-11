from typing import Optional

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField, MonitorField

from communikit.communities.models import Community


class JoinRequest(TimeStampedModel):
    STATUS = Choices(
        ("pending", _("Pending")),
        ("accepted", _("Accepted")),
        ("rejected", _("Rejected")),
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    email = models.EmailField(null=True, blank=True)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    status = StatusField(db_index=True)
    status_changed = MonitorField(monitor="status")

    sent = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("email", "community", "sender")

    def __str__(self) -> str:
        return self.email or self.sender.email

    def get_sender(self) -> Optional[settings.AUTH_USER_MODEL]:
        qs = get_user_model()._default_manager
        if self.sender_id:
            qs = qs.filter(pk=self.sender_id)
        else:
            qs = qs.filter(
                models.Q(emailaddress__email__iexact=self.email)
                | models.Q(email__iexact=self.email)
            )
        return qs.first()

    def is_pending(self) -> bool:
        return self.status == self.STATUS.pending

    def is_accepted(self) -> bool:
        return self.status == self.STATUS.accepted

    def is_rejected(self) -> bool:
        return self.status == self.STATUS.rejected
