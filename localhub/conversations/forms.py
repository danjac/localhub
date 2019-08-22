# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.conversations.models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("message",)
        labels = {"message": _("Send Message")}
