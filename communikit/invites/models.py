# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel

from communikit.communities.models import Community


class Invite(TimeStampedModel):
    STATUS = Choices(
        ("pending", _("Pending")),
        ("accepted", _("Accepted")),
        ("rejected", _("Rejected")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    status = StatusField(db_index=True)
    status_changed = MonitorField(monitor="status")

    sent = models.DateTimeField(null=True, blank=True)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("email", "community")

    def __str__(self) -> str:
        return self.email

    def is_pending(self) -> bool:
        return self.status == self.STATUS.pending

    def is_accepted(self) -> bool:
        return self.status == self.STATUS.accepted

    def is_rejected(self) -> bool:
        return self.status == self.STATUS.rejected
