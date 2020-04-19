# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import forms
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MaxLengthValidator
from django.utils.translation import gettext_lazy as _

from localhub.users.forms import MentionsField
from localhub.users.utils import extract_mentions

from .models import Message


class MessageForm(forms.ModelForm):

    recipient = MentionsField(
        required=True,
        help_text=_("Look up recipient with @username"),
        validators=[MaxLengthValidator(60)],
    )

    class Meta:
        model = Message
        fields = (
            "recipient",
            "message",
        )
        labels = {"message": _("Send Message")}

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
