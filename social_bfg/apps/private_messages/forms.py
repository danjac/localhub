# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

# Social-BFG
from social_bfg.apps.users.forms import MentionsField
from social_bfg.apps.users.utils import extract_mentions

# Local
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("message",)


class MessageRecipientForm(MessageForm):
    """Adds an extra recipient field to allow sender to lookup
    a recipient for this message.
    """

    recipient = MentionsField(
        required=True, help_text=_("Use @mention format to find and add a recipient"),
    )

    class Meta(MessageForm.Meta):
        fields = (
            "recipient",
            "message",
        )

    def __init__(self, *args, **kwargs):
        self.community = kwargs.pop("community", None)
        self.sender = kwargs.pop("sender", None)
        super().__init__(*args, **kwargs)

    def clean_recipient(self):
        if self.community is None:
            raise ImproperlyConfigured(
                "community must be provided if recipient field is used"
            )
        if self.sender is None:
            raise ImproperlyConfigured(
                "sender must be provided if recipient field is used"
            )
        # validate that all mentioned recipients are community members
        usernames = extract_mentions(self.cleaned_data["recipient"])
        if len(usernames) > 1:
            raise ValidationError(_("You can only select one recipient at a time"))
        recipient = (
            self.community.get_members()
            .matches_usernames(usernames)
            .exclude_blocking(self.sender)
            .exclude(pk=self.sender.pk)
            .first()
        )
        if recipient is None:
            raise ValidationError(_("No active member found matching this name"))
        return recipient
