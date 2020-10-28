# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Third Party Libraries
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel

# Localhub
from localhub.common.db.search.mixins import SearchQuerySetMixin
from localhub.communities.models import Community


class JoinRequestQuerySet(SearchQuerySetMixin, models.QuerySet):
    search_document_field = "sender__search_document"

    def for_sender(self, user):
        return self.filter(sender=user).exclude(community__members=user)

    def for_community(self, community):
        return self.filter(community=community)

    def pending(self):
        return self.filter(status=self.model.Status.PENDING)

    def accepted(self):
        return self.filter(status=self.model.Status.ACCEPTED)

    def rejected(self):
        return self.filter(status=self.model.Status.REJECTED)


class JoinRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        REJECTED = "rejected", _("Rejected")

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=100, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    status_changed = MonitorField(monitor="status")

    sent = models.DateTimeField(null=True, blank=True)

    intro = models.TextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_(
            "Tell us a little bit about yourself and why you "
            "would like to join this community (Optional)."
        ),
    )

    objects = JoinRequestQuerySet.as_manager()

    class Meta:
        unique_together = ("community", "sender")
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return str(self.sender)

    def get_absolute_url(self):
        return reverse("join_requests:detail", args=[self.id])

    def is_pending(self):
        return self.status == self.Status.PENDING

    def is_accepted(self):
        return self.status == self.Status.ACCEPTED

    def is_rejected(self):
        return self.status == self.Status.REJECTED

    def accept(self):
        self.status = JoinRequest.Status.ACCEPTED
        self.save()

    def reject(self):
        self.status = JoinRequest.Status.REJECTED
        self.save()
