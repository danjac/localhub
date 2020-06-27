# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import forms

# Local
from .models import Flag


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ("reason",)
        widgets = {"reason": forms.RadioSelect}
