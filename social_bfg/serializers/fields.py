# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# https://github.com/mfogel/django-timezone-field/issues/29

# Django Rest Framework
from rest_framework import serializers

# Third Party Libraries
from timezone_field import TimeZoneField as TimeZoneField_


class TimeZoneField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(TimeZoneField_.CHOICES + [(None, "")], **kwargs)

    def to_representation(self, value):
        return str(super().to_representation(value))
