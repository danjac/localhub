# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField, MonitorField

from localhub.communities.models import Community


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
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        if self.sender_id:
            return self.sender.email
        return self.email

    def get_sender(self):
        qs = get_user_model()._default_manager
        if self.sender_id:
            qs = qs.filter(pk=self.sender_id)
        else:
            qs = qs.for_email(self.email)
        return qs.first()

    def is_pending(self):
        return self.status == self.STATUS.pending

    def is_accepted(self):
        return self.status == self.STATUS.accepted

    def is_rejected(self):
        return self.status == self.STATUS.rejected
