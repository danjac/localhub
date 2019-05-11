from django.db import models
from django.conf import settings
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

    def clean(self):
        if not any((self.email, self.sender_id)):
            raise ValidationError(_("Must include email or current user"))

    def is_pending(self) -> bool:
        return self.status == self.STATUS.pending

    def is_accepted(self) -> bool:
        return self.status == self.STATUS.accepted

    def is_rejected(self) -> bool:
        return self.status == self.STATUS.rejected
