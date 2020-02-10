# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.db.search import SearchQuerySetMixin


class JoinRequestQuerySet(SearchQuerySetMixin, models.QuerySet):
    search_document_field = "sender__search_document"


class JoinRequest(TimeStampedModel):
    STATUS = Choices(
        ("pending", _("Pending")),
        ("accepted", _("Accepted")),
        ("rejected", _("Rejected")),
    )

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    status = StatusField(db_index=True)
    status_changed = MonitorField(monitor="status")

    sent = models.DateTimeField(null=True, blank=True)

    intro = models.TextField(
        blank=True,
        help_text=_(
            "Tell us a little bit about yourself and why you "
            "would like to join this community (Optional)"
        ),
    )

    objects = JoinRequestQuerySet.as_manager()

    class Meta:
        unique_together = ("community", "sender")
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return str(self.sender)

    def get_absolute_url(self):
        return reverse("joinrequests:detail", args=[self.id])

    def is_pending(self):
        return self.status == self.STATUS.pending

    def is_accepted(self):
        return self.status == self.STATUS.accepted

    def is_rejected(self):
        return self.status == self.STATUS.rejected
