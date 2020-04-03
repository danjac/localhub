# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Invite


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ("email",)

    def __init__(self, community, *args, **kwargs):
        self.community = community
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if self.community.members.for_email(email).exists():
            raise ValidationError(
                _("A user with this email address already belongs to " "this community")
            )
        if Invite.objects.filter(
            email__iexact=email, community=self.community
        ).exists():
            raise ValidationError(
                _("An invitation has already been sent to this email address")
            )
        return email
