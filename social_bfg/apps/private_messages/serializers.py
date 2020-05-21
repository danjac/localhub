# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django Rest Framework
from rest_framework import serializers

# Social-BFG
from social_bfg.apps.users.serializers import UserSerializer

# Local
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    markdown = serializers.SerializerMethodField()

    # annotated fields

    is_new = serializers.BooleanField(read_only=True)

    # re annotated fields: it might be more efficient long-term
    # to load/update bookmarks, likes etc as PK/object types per user
    # rather than pull with annotated queries. For now this is OK
    # but let's revisit.
    has_bookmarked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "sender",
            "recipient",
            "message",
            "markdown",
            "parent",
            "created",
            "is_new",
            "has_bookmarked",
        )

    def get_markdown(self, obj):
        return obj.message.markdown()
