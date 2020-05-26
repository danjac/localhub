# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth import get_user_model

# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.serializers.fields import TimeZoneField


class UserSerializer(serializers.ModelSerializer):
    """Shows minimal info on users"""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "name",
            "full_name",
            "avatar",
            "bio",
        )

    def get_full_name(self, obj):
        return obj.name or obj.username


class AuthenticatedUserSerializer(UserSerializer):
    """Complete info on current auth user """

    default_timezone = TimeZoneField()
    roles = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "language",
            "default_timezone",
            "send_email_notifications",
            "activity_stream_filters",
            "show_sensitive_content",
            "show_external_images",
            "show_embedded_content",
            "roles",
        )

    def get_roles(self, obj):
        return obj.member_cache.roles
