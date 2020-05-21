# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Third Party Libraries
from django_countries.serializer_fields import CountryField

# Social-BFG
from social_bfg.apps.activities.serializers import ActivitySerializer
from social_bfg.serializers.fields import TimeZoneField

# Local
from .models import Event


class EventSerializer(ActivitySerializer):

    country = CountryField()
    timezone = TimeZoneField()

    location = serializers.SerializerMethodField()
    full_location = serializers.SerializerMethodField()

    # annotated fields
    next_date = serializers.DateTimeField(read_only=True)
    num_attendees = serializers.IntegerField(read_only=True)
    is_attending = serializers.BooleanField(read_only=True)

    class Meta(ActivitySerializer.Meta):
        model = Event
        fields = ActivitySerializer.Meta.fields + (
            "starts",
            "ends",
            "repeats",
            "repeats_until",
            "canceled",
            "url",
            "latitude",
            "longitude",
            "street_address",
            "locality",
            "postal_code",
            "region",
            "country",
            "timezone",
            "venue",
            "next_date",
            "is_attending",
            "num_attendees",
            "location",
            "full_location",
        )

        read_only_fields = (
            "canceled",
            "latitude",
            "longitude",
        )

    def get_location(self, obj):
        return obj.get_location()

    def get_full_location(self, obj):
        return obj.get_full_location()
