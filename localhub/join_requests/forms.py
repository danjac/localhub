# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from localhub.join_requests.models import JoinRequest


class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ("email",)

    def __init__(self, community, sender, *args, **kwargs):
        self.community = community
        self.sender = sender

        super().__init__(*args, **kwargs)

        if self.sender:
            del self.fields["email"]

    def clean(self):
        data = super().clean()

        email = self.sender.email if self.sender else data["email"]
        if self.community.is_email_blacklisted(email):
            raise ValidationError(
                _(
                    "Sorry, we cannot accept your application "
                    "to join at this time."
                )
            )

        if self.sender:
            qs = self.community.members.filter(pk=self.sender.id)
        else:
            qs = self.community.members.filter(email__iexact=data["email"])

        if qs.exists():
            raise ValidationError(_("You already belong to this community."))

        if self.sender:
            qs = JoinRequest.objects.filter(sender=self.sender)
        else:
            qs = JoinRequest.objects.filter(email__iexact=data["email"])

        if qs.exists():
            raise ValidationError(
                _("You have already sent a request. Be patient.")
            )

        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sender = self.sender
        instance.community = self.community
        if commit:
            instance.save()
        return instance
