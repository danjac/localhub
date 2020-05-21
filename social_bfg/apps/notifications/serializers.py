# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.users.serializers import UserSerializer
from social_bfg.serializers import GenericObjectSerializer

# Local
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    actor = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    content_object = GenericObjectSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "actor",
            "recipient",
            "content_object",
            "verb",
        )
