# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms

from .widgets import CalendarWidget


class CalendarField(forms.SplitDateTimeField):
    widget = CalendarWidget
