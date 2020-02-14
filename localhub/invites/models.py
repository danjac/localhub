# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel

from localhub.communities.models import Community


class InviteQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(email__in=user.get_email_addresses())

    def pending(self):
        return self.filter(status=self.model.STATUS.pending)

    def accepted(self):
        return self.filter(status=self.model.STATUS.accepted)

    def rejected(self):
        return self.filter(status=self.model.STATUS.rejected)


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

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    objects = InviteQuerySet.as_manager()

    class Meta:
        unique_together = ("email", "community")

    def __str__(self):
        return self.email

    def is_pending(self):
        return self.status == self.STATUS.pending

    def is_accepted(self):
        return self.status == self.STATUS.accepted

    def is_rejected(self):
        return self.status == self.STATUS.rejected

    def get_recipient(self):
        return get_user_model().objects.for_email(self.email).first()
