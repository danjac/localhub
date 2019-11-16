# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms

from localhub.polls.models import Poll


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ("title", "description", "allow_comments")
