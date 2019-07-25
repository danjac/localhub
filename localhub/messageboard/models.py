# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField


class Message(TimeStampedModel):

    subject = models.CharField(max_length=200)

    message = MarkdownField(blank=True)

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
    )

    def __str__(self) -> str:
        return self.subject

    def get_absolute_url(self) -> str:
        return reverse("messageboard:message_detail", args=[self.id])


class MessageRecipient(models.Model):

    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    read = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "message"],
                name="unique_message_recipient",
            )
        ]

    def __str__(self) -> str:
        return str(self.message)

    def get_absolute_url(self) -> str:
        return reverse("messageboard:message_recipient_detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.message.community.resolve_url(self.get_absolute_url())
